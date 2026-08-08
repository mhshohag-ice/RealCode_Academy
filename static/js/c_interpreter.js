/*
 * Minimal embedded-C subset interpreter for RealCode Academy's Learn C lessons.
 * Not a general-purpose C compiler: supports just enough of C (types, if/else,
 * for/while, one level of user functions, printf, and a fixed set of
 * hardware builtins) to run real embedded-systems teaching examples and
 * produce a step-by-step execution trace for UI playback, mirroring the
 * Python lesson's sys.settrace-based engine.
 */
(function (root) {
  'use strict';

  /* ---------------- Lexer ---------------- */

  const KEYWORDS = new Set(['int', 'float', 'char', 'void', 'if', 'else', 'for', 'while', 'return']);

  function tokenize(src) {
    const tokens = [];
    let i = 0;
    let line = 1;
    const n = src.length;

    function peekStr(s) {
      return src.startsWith(s, i);
    }

    while (i < n) {
      const c = src[i];

      if (c === '\n') { line++; i++; continue; }
      if (c === ' ' || c === '\t' || c === '\r') { i++; continue; }

      // preprocessor line, e.g. #include <stdio.h>
      if (c === '#') {
        while (i < n && src[i] !== '\n') i++;
        continue;
      }

      // line comment
      if (peekStr('//')) {
        while (i < n && src[i] !== '\n') i++;
        continue;
      }

      // block comment
      if (peekStr('/*')) {
        i += 2;
        while (i < n && !peekStr('*/')) { if (src[i] === '\n') line++; i++; }
        i += 2;
        continue;
      }

      // string literal
      if (c === '"') {
        const startLine = line;
        i++;
        let s = '';
        while (i < n && src[i] !== '"') {
          if (src[i] === '\\' && i + 1 < n) {
            const esc = src[i + 1];
            s += esc === 'n' ? '\n' : esc === 't' ? '\t' : esc === '"' ? '"' : esc === '\\' ? '\\' : esc;
            i += 2;
          } else {
            s += src[i];
            i++;
          }
        }
        i++; // closing quote
        tokens.push({ type: 'string', value: s, line: startLine });
        continue;
      }

      // number literal
      if (/[0-9]/.test(c)) {
        const start = i;
        while (i < n && /[0-9]/.test(src[i])) i++;
        if (src[i] === '.' && /[0-9]/.test(src[i + 1] || '')) {
          i++;
          while (i < n && /[0-9]/.test(src[i])) i++;
        }
        tokens.push({ type: 'number', value: parseFloat(src.slice(start, i)), line });
        continue;
      }

      // identifier / keyword
      if (/[A-Za-z_]/.test(c)) {
        const start = i;
        while (i < n && /[A-Za-z0-9_]/.test(src[i])) i++;
        const word = src.slice(start, i);
        tokens.push({ type: KEYWORDS.has(word) ? 'keyword' : 'ident', value: word, line });
        continue;
      }

      // multi-char operators
      const three = src.slice(i, i + 2);
      const multiOps = ['==', '!=', '<=', '>=', '&&', '||', '+=', '-=', '*=', '/=', '++', '--'];
      if (multiOps.includes(three)) {
        tokens.push({ type: 'op', value: three, line });
        i += 2;
        continue;
      }

      // single-char operators/punctuation
      if ('(){};,+-*/%<>=!.'.includes(c)) {
        tokens.push({ type: 'op', value: c, line });
        i++;
        continue;
      }

      throw new Error(`Unexpected character '${c}' on line ${line}`);
    }

    tokens.push({ type: 'eof', value: null, line });
    return tokens;
  }

  /* ---------------- Parser ---------------- */

  class Parser {
    constructor(tokens) {
      this.tokens = tokens;
      this.pos = 0;
    }
    peek(offset = 0) { return this.tokens[this.pos + offset]; }
    next() { return this.tokens[this.pos++]; }
    at(type, value) {
      const t = this.peek();
      return t.type === type && (value === undefined || t.value === value);
    }
    expect(type, value) {
      if (!this.at(type, value)) {
        const t = this.peek();
        throw new Error(`Line ${t.line}: expected ${value || type}, got '${t.value}'`);
      }
      return this.next();
    }
    isType() {
      return this.at('keyword', 'int') || this.at('keyword', 'float') || this.at('keyword', 'char') || this.at('keyword', 'void');
    }

    parseProgram() {
      const decls = [];
      while (!this.at('eof')) {
        if (!this.isType()) throw new Error(`Line ${this.peek().line}: expected a type declaration`);
        const save = this.pos;
        this.next(); // type
        this.expect('ident'); // name
        const isFunc = this.at('op', '(');
        this.pos = save;
        if (isFunc) {
          decls.push(this.parseFunctionDecl());
        } else {
          const d = this.parseVarDecl();
          this.expect('op', ';');
          decls.push(d);
        }
      }
      return { type: 'Program', decls };
    }

    parseFunctionDecl() {
      const typeTok = this.next(); // return type
      const nameTok = this.expect('ident');
      this.expect('op', '(');
      const params = [];
      if (!this.at('op', ')')) {
        do {
          const pType = this.next().value;
          const pName = this.expect('ident').value;
          params.push({ type: pType, name: pName });
        } while (this.at('op', ',') && this.next());
      }
      this.expect('op', ')');
      const body = this.parseBlock();
      return { type: 'FunctionDecl', name: nameTok.value, returnType: typeTok.value, params, body, line: nameTok.line };
    }

    parseBlock() {
      this.expect('op', '{');
      const statements = [];
      while (!this.at('op', '}')) statements.push(this.parseStatement());
      this.expect('op', '}');
      return { type: 'Block', statements };
    }

    parseStatement() {
      if (this.at('op', '{')) return this.parseBlock();
      if (this.isType()) { const d = this.parseVarDecl(); this.expect('op', ';'); return d; }
      if (this.at('keyword', 'if')) return this.parseIf();
      if (this.at('keyword', 'for')) return this.parseFor();
      if (this.at('keyword', 'while')) return this.parseWhile();
      if (this.at('keyword', 'return')) {
        const line = this.next().line;
        const expr = this.at('op', ';') ? null : this.parseExpr();
        this.expect('op', ';');
        return { type: 'Return', expr, line };
      }
      const line = this.peek().line;
      const expr = this.parseExpr();
      this.expect('op', ';');
      return { type: 'ExprStmt', expr, line };
    }

    parseVarDecl() {
      const line = this.peek().line;
      const varType = this.next().value;
      const name = this.expect('ident').value;
      let init = null;
      if (this.at('op', '=')) { this.next(); init = this.parseExpr(); }
      return { type: 'VarDecl', varType, name, init, line };
    }

    parseIf() {
      const line = this.next().line; // 'if'
      this.expect('op', '(');
      const cond = this.parseExpr();
      this.expect('op', ')');
      const then = this.parseBlock();
      let elseBranch = null;
      if (this.at('keyword', 'else')) {
        this.next();
        elseBranch = this.at('keyword', 'if') ? this.parseIf() : this.parseBlock();
      }
      return { type: 'If', cond, then, else: elseBranch, line };
    }

    parseFor() {
      const line = this.next().line; // 'for'
      this.expect('op', '(');
      let init = null;
      if (!this.at('op', ';')) init = this.isType() ? this.parseVarDecl() : { type: 'ExprStmt', expr: this.parseExpr(), line: this.peek().line };
      this.expect('op', ';');
      let cond = null;
      if (!this.at('op', ';')) cond = this.parseExpr();
      this.expect('op', ';');
      let update = null;
      if (!this.at('op', ')')) update = this.parseExpr();
      this.expect('op', ')');
      const body = this.parseBlock();
      return { type: 'For', init, cond, update, body, line };
    }

    parseWhile() {
      const line = this.next().line; // 'while'
      this.expect('op', '(');
      const cond = this.parseExpr();
      this.expect('op', ')');
      const body = this.parseBlock();
      return { type: 'While', cond, body, line };
    }

    parseExpr() { return this.parseAssign(); }

    parseAssign() {
      if (this.at('ident') && ['=', '+=', '-=', '*=', '/='].includes((this.peek(1) || {}).value)) {
        const nameTok = this.next();
        const opTok = this.next();
        const value = this.parseAssign();
        return { type: 'Assign', name: nameTok.value, op: opTok.value, value, line: nameTok.line };
      }
      return this.parseLogicalOr();
    }
    parseLogicalOr() {
      let left = this.parseLogicalAnd();
      while (this.at('op', '||')) { const op = this.next().value; left = { type: 'Binary', op, left, right: this.parseLogicalAnd() }; }
      return left;
    }
    parseLogicalAnd() {
      let left = this.parseEquality();
      while (this.at('op', '&&')) { const op = this.next().value; left = { type: 'Binary', op, left, right: this.parseEquality() }; }
      return left;
    }
    parseEquality() {
      let left = this.parseRelational();
      while (this.at('op', '==') || this.at('op', '!=')) { const op = this.next().value; left = { type: 'Binary', op, left, right: this.parseRelational() }; }
      return left;
    }
    parseRelational() {
      let left = this.parseAdditive();
      while (['<', '>', '<=', '>='].includes(this.peek().value) && this.peek().type === 'op') {
        const op = this.next().value; left = { type: 'Binary', op, left, right: this.parseAdditive() };
      }
      return left;
    }
    parseAdditive() {
      let left = this.parseMultiplicative();
      while (this.at('op', '+') || this.at('op', '-')) { const op = this.next().value; left = { type: 'Binary', op, left, right: this.parseMultiplicative() }; }
      return left;
    }
    parseMultiplicative() {
      let left = this.parseUnary();
      while (this.at('op', '*') || this.at('op', '/') || this.at('op', '%')) { const op = this.next().value; left = { type: 'Binary', op, left, right: this.parseUnary() }; }
      return left;
    }
    parseUnary() {
      if (this.at('op', '-') || this.at('op', '!')) { const op = this.next().value; return { type: 'Unary', op, expr: this.parseUnary() }; }
      return this.parsePostfix();
    }
    parsePostfix() {
      let node = this.parsePrimary();
      if ((this.at('op', '++') || this.at('op', '--')) && node.type === 'Ident') {
        const op = this.next().value;
        return { type: 'PostfixIncDec', name: node.name, op, line: node.line };
      }
      return node;
    }
    parsePrimary() {
      const t = this.peek();
      if (t.type === 'number') { this.next(); return { type: 'Num', value: t.value, line: t.line }; }
      if (t.type === 'string') { this.next(); return { type: 'Str', value: t.value, line: t.line }; }
      if (t.type === 'op' && t.value === '(') { this.next(); const e = this.parseExpr(); this.expect('op', ')'); return e; }
      if (t.type === 'ident') {
        this.next();
        let name = t.value;
        while (this.at('op', '.')) {
          this.next();
          name += '.' + this.expect('ident').value;
        }
        if (this.at('op', '(')) {
          this.next();
          const args = [];
          if (!this.at('op', ')')) {
            do { args.push(this.parseExpr()); } while (this.at('op', ',') && this.next());
          }
          this.expect('op', ')');
          return { type: 'Call', name, args, line: t.line };
        }
        return { type: 'Ident', name, line: t.line };
      }
      throw new Error(`Line ${t.line}: unexpected token '${t.value}'`);
    }
  }

  /* ---------------- Hardware builtins ---------------- */

  const HW_BUILTINS = {
    read_distance_cm: { kind: 'sensor', sensorKind: 'distance' },
    read_light_level: { kind: 'sensor', sensorKind: 'light' },
    read_temperature_c: { kind: 'sensor', sensorKind: 'temperature' },
    led_on: { kind: 'actuator', device: 'led', state: 'on' },
    led_off: { kind: 'actuator', device: 'led', state: 'off' },
    buzzer_on: { kind: 'actuator', device: 'buzzer', state: 'on' },
    buzzer_off: { kind: 'actuator', device: 'buzzer', state: 'off' },
    set_motor_speed: { kind: 'actuator_arg', device: 'motor' },
    printf: { kind: 'print' },

    pinMode: { kind: 'pin_mode' },
    digitalWrite: { kind: 'pin_write' },
    analogRead: { kind: 'pin_read' },
    digitalRead: { kind: 'pin_read' },
    delay: { kind: 'noop' },
    'Serial.begin': { kind: 'noop' },
    'Serial.print': { kind: 'serial_print' },
    'Serial.println': { kind: 'serial_print' },
  };

  function formatPrintf(fmt, args) {
    let ai = 0;
    let out = '';
    for (let i = 0; i < fmt.length; i++) {
      if (fmt[i] === '%' && i + 1 < fmt.length) {
        const spec = fmt[i + 1];
        if (spec === 'd') { out += String(Math.trunc(args[ai++])); i++; continue; }
        if (spec === 'f') { out += Number(args[ai++]).toFixed(2); i++; continue; }
        if (spec === 's') { out += String(args[ai++]); i++; continue; }
        if (spec === '%') { out += '%'; i++; continue; }
      }
      out += fmt[i];
    }
    return out;
  }

  /* ---------------- Interpreter ---------------- */

  class CRuntimeError extends Error {}

  function run(source, options) {
    options = options || {};
    const readSensor = options.readSensor || (() => 0);

    const steps = [];
    let outputBuf = '';

    function fmtVal(v, type) {
      if (typeof v !== 'number') return String(v);
      if (type === 'float') return Number.isInteger(v) ? v.toFixed(1) : String(v);
      return String(Math.trunc(v));
    }

    function snapshot(frame) {
      const out = {};
      for (const name of Object.keys(frame.vars)) {
        out[name] = fmtVal(frame.vars[name].value, frame.vars[name].type);
      }
      return out;
    }

    function recordStep(line, event, frame, extra) {
      const step = { line, event, func: frame.name, locals: snapshot(frame) };
      if (extra && extra.hw) step.hw = extra.hw;
      if (extra && extra.output) {
        outputBuf += extra.output + '\n';
        step.output = extra.output;
      }
      steps.push(step);
      return step;
    }

    function lookup(frame, globalFrame, name) {
      if (name in frame.vars) return frame.vars[name];
      if (frame !== globalFrame && name in globalFrame.vars) return globalFrame.vars[name];
      throw new CRuntimeError(`Undeclared variable '${name}'`);
    }

    let funcTable = {};

    function evalExpr(node, frame, globalFrame) {
      switch (node.type) {
        case 'Num': return { value: node.value, type: Number.isInteger(node.value) ? 'int' : 'float', hw: null, output: null };
        case 'Str': return { value: node.value, type: 'string', hw: null, output: null };
        case 'Ident': { const v = lookup(frame, globalFrame, node.name); return { value: v.value, type: v.type, hw: null, output: null }; }
        case 'Unary': {
          const r = evalExpr(node.expr, frame, globalFrame);
          const value = node.op === '-' ? -r.value : (r.value === 0 ? 1 : 0);
          return { value, type: r.type, hw: r.hw, output: r.output };
        }
        case 'Binary': {
          const l = evalExpr(node.left, frame, globalFrame);
          const r = evalExpr(node.right, frame, globalFrame);
          const rt = (l.type === 'float' || r.type === 'float') ? 'float' : 'int';
          let value;
          switch (node.op) {
            case '+': value = l.value + r.value; break;
            case '-': value = l.value - r.value; break;
            case '*': value = l.value * r.value; break;
            case '/': value = rt === 'int' ? Math.trunc(l.value / r.value) : l.value / r.value; break;
            case '%': value = l.value % r.value; break;
            case '<': return { value: l.value < r.value ? 1 : 0, type: 'int', hw: null, output: null };
            case '>': return { value: l.value > r.value ? 1 : 0, type: 'int', hw: null, output: null };
            case '<=': return { value: l.value <= r.value ? 1 : 0, type: 'int', hw: null, output: null };
            case '>=': return { value: l.value >= r.value ? 1 : 0, type: 'int', hw: null, output: null };
            case '==': return { value: l.value === r.value ? 1 : 0, type: 'int', hw: null, output: null };
            case '!=': return { value: l.value !== r.value ? 1 : 0, type: 'int', hw: null, output: null };
            case '&&': return { value: (l.value !== 0 && r.value !== 0) ? 1 : 0, type: 'int', hw: null, output: null };
            case '||': return { value: (l.value !== 0 || r.value !== 0) ? 1 : 0, type: 'int', hw: null, output: null };
            default: throw new CRuntimeError(`Unknown operator ${node.op}`);
          }
          return { value, type: rt, hw: null, output: null };
        }
        case 'Assign': {
          const target = lookup(frame, globalFrame, node.name);
          const r = evalExpr(node.value, frame, globalFrame);
          let value;
          if (node.op === '=') value = r.value;
          else if (node.op === '+=') value = target.value + r.value;
          else if (node.op === '-=') value = target.value - r.value;
          else if (node.op === '*=') value = target.value * r.value;
          else if (node.op === '/=') value = target.value / r.value;
          target.value = target.type === 'int' ? Math.trunc(value) : value;
          return { value: target.value, type: target.type, hw: r.hw, output: r.output };
        }
        case 'PostfixIncDec': {
          const target = lookup(frame, globalFrame, node.name);
          const old = target.value;
          target.value += node.op === '++' ? 1 : -1;
          return { value: old, type: target.type, hw: null, output: null };
        }
        case 'Call': return evalCall(node, frame, globalFrame);
        default: throw new CRuntimeError(`Unknown expression node ${node.type}`);
      }
    }

    function evalArgs(args, frame, globalFrame) {
      const values = [];
      let hw = null, output = null;
      for (const a of args) {
        const r = evalExpr(a, frame, globalFrame);
        values.push(r.value);
        if (r.hw) hw = r.hw;
        if (r.output) output = (output ? output + ' ' : '') + r.output;
      }
      return { values, hw, output };
    }

    function evalCall(node, frame, globalFrame) {
      const { values: args } = evalArgs(node.args, frame, globalFrame);

      if (HW_BUILTINS[node.name]) {
        const spec = HW_BUILTINS[node.name];
        if (spec.kind === 'sensor') {
          const v = readSensor(spec.sensorKind);
          return { value: v, type: 'int', hw: { type: 'sensor_read', sensorKind: spec.sensorKind, value: v }, output: null };
        }
        if (spec.kind === 'actuator') {
          return { value: 0, type: 'int', hw: { type: 'actuator', device: spec.device, state: spec.state }, output: null };
        }
        if (spec.kind === 'actuator_arg') {
          return { value: 0, type: 'int', hw: { type: 'actuator', device: spec.device, value: args[0] }, output: null };
        }
        if (spec.kind === 'print') {
          const text = formatPrintf(String(args[0]), args.slice(1)).replace(/\n$/, '');
          return { value: 0, type: 'int', hw: null, output: text };
        }
        if (spec.kind === 'pin_mode') {
          return { value: 0, type: 'int', hw: { type: 'pin_mode', pin: args[0], mode: args[1] }, output: null };
        }
        if (spec.kind === 'pin_write') {
          return { value: 0, type: 'int', hw: { type: 'pin_write', pin: args[0], value: args[1] }, output: null };
        }
        if (spec.kind === 'pin_read') {
          const v = readSensor(args[0]);
          return { value: v, type: 'int', hw: { type: 'pin_read', pin: args[0], value: v }, output: null };
        }
        if (spec.kind === 'noop') {
          return { value: 0, type: 'int', hw: null, output: null };
        }
        if (spec.kind === 'serial_print') {
          const text = args.map(String).join('');
          return { value: 0, type: 'int', hw: null, output: text };
        }
      }

      const fn = funcTable[node.name];
      if (!fn) throw new CRuntimeError(`Call to undeclared function '${node.name}' on line ${node.line}`);

      const newFrame = { name: fn.name, vars: {} };
      fn.params.forEach((p, idx) => { newFrame.vars[p.name] = { value: args[idx], type: p.type }; });
      recordStep(fn.line, 'call', newFrame);

      const result = execBlock(fn.body, newFrame, globalFrame);
      recordStep(result.returnLine != null ? result.returnLine : fn.line, 'return', newFrame);

      return { value: result.value != null ? result.value : 0, type: fn.returnType === 'float' ? 'float' : 'int', hw: null, output: null };
    }

    // Returns { returned: bool, value, returnLine }
    function execBlock(block, frame, globalFrame) {
      for (const stmt of block.statements) {
        const r = execStatement(stmt, frame, globalFrame);
        if (r && r.returned) return r;
      }
      return { returned: false };
    }

    function execStatement(stmt, frame, globalFrame) {
      switch (stmt.type) {
        case 'Block':
          return execBlock(stmt, frame, globalFrame);

        case 'VarDecl': {
          let value = 0, hw = null, output = null;
          if (stmt.init) { const r = evalExpr(stmt.init, frame, globalFrame); value = r.value; hw = r.hw; output = r.output; }
          frame.vars[stmt.name] = { value: stmt.varType === 'int' ? Math.trunc(value) : value, type: stmt.varType };
          recordStep(stmt.line, 'line', frame, { hw, output });
          return null;
        }

        case 'ExprStmt': {
          const r = evalExpr(stmt.expr, frame, globalFrame);
          recordStep(stmt.line, 'line', frame, { hw: r.hw, output: r.output });
          return null;
        }

        case 'If': {
          const cond = evalExpr(stmt.cond, frame, globalFrame);
          recordStep(stmt.line, 'line', frame, { hw: cond.hw, output: cond.output });
          if (cond.value !== 0) return execBlock(stmt.then, frame, globalFrame);
          if (stmt.else) return stmt.else.type === 'If' ? execStatement(stmt.else, frame, globalFrame) : execBlock(stmt.else, frame, globalFrame);
          return null;
        }

        case 'For': {
          if (stmt.init) execStatement(stmt.init, frame, globalFrame);
          while (true) {
            let condVal = 1, hw = null, output = null;
            if (stmt.cond) { const c = evalExpr(stmt.cond, frame, globalFrame); condVal = c.value; hw = c.hw; output = c.output; }
            recordStep(stmt.line, 'line', frame, { hw, output });
            if (condVal === 0) break;
            const r = execBlock(stmt.body, frame, globalFrame);
            if (r && r.returned) return r;
            if (stmt.update) evalExpr(stmt.update, frame, globalFrame);
          }
          return null;
        }

        case 'While': {
          while (true) {
            const c = evalExpr(stmt.cond, frame, globalFrame);
            recordStep(stmt.line, 'line', frame, { hw: c.hw, output: c.output });
            if (c.value === 0) break;
            const r = execBlock(stmt.body, frame, globalFrame);
            if (r && r.returned) return r;
          }
          return null;
        }

        case 'Return': {
          let value = null, hw = null, output = null;
          if (stmt.expr) { const r = evalExpr(stmt.expr, frame, globalFrame); value = r.value; hw = r.hw; output = r.output; }
          recordStep(stmt.line, 'line', frame, { hw, output });
          return { returned: true, value, returnLine: stmt.line };
        }

        default:
          throw new CRuntimeError(`Unknown statement ${stmt.type}`);
      }
    }

    const ARDUINO_LOOP_ITERATIONS = 3;

    let error = null;
    try {
      const tokens = tokenize(source);
      const program = new Parser(tokens).parseProgram();
      funcTable = {};
      program.decls.forEach((d) => { if (d.type === 'FunctionDecl') funcTable[d.name] = d; });

      const globalFrame = {
        name: '<global>',
        vars: {
          HIGH: { value: 1, type: 'int' },
          LOW: { value: 0, type: 'int' },
          OUTPUT: { value: 1, type: 'int' },
          INPUT: { value: 0, type: 'int' },
          LED_BUILTIN: { value: 13, type: 'int' },
          A0: { value: 14, type: 'int' },
          A1: { value: 15, type: 'int' },
          A2: { value: 16, type: 'int' },
          A3: { value: 17, type: 'int' },
          A4: { value: 18, type: 'int' },
          A5: { value: 19, type: 'int' },
        },
      };

      program.decls.forEach((d) => {
        if (d.type === 'VarDecl') execStatement(d, globalFrame, globalFrame);
      });

      function runFunction(fn, frameName) {
        const frame = { name: frameName, vars: {} };
        recordStep(fn.line, 'call', frame);
        const result = execBlock(fn.body, frame, globalFrame);
        recordStep(result.returnLine != null ? result.returnLine : fn.line, 'return', frame);
      }

      if (funcTable.main) {
        runFunction(funcTable.main, 'main');
      } else if (funcTable.setup && funcTable.loop) {
        runFunction(funcTable.setup, 'setup');
        for (let i = 0; i < ARDUINO_LOOP_ITERATIONS; i++) {
          runFunction(funcTable.loop, 'loop');
        }
      } else {
        throw new CRuntimeError('No main() or setup()/loop() found');
      }
    } catch (e) {
      error = e.message;
    }

    return { steps, output: outputBuf, error };
  }

  const CInterpreter = { run };

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = CInterpreter;
  } else {
    root.CInterpreter = CInterpreter;
  }
})(typeof window !== 'undefined' ? window : globalThis);
