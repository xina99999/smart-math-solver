# 📋 RULES GUIDE - Hướng dẫn viết & maintain diagnostic rules

## 📑 Mục lục
1. [Cấu trúc Rules](#cấu-trúc-rules)
2. [Viết Regex Patterns](#viết-regex-patterns)
3. [Ví dụ chi tiết](#ví-dụ-chi-tiết)
4. [Best Practices](#best-practices)
5. [Testing Rules](#testing-rules)

---

## 🏗️ Cấu trúc Rules

### Toàn bộ cấu trúc file

```json
{
  "meta": {...},
  "knowledge_model": "string",
  "topic_keywords": {...},
  "diagnostic_rules": [
    {
      "id": "R_RULE_NAME",
      "severity": "critical|high|medium|low",
      "category": "category_name",
      "error_type": "Tên lỗi",
      "why_it_happens": "Giải thích nguyên nhân",
      "fix_summary": "Tóm tắt cách sửa",
      "patterns": [
        {
          "regex": "pattern_here",
          "name": "Human readable name",
          "explanation": "Giải thích pattern này làm gì",
          "evidence": "Thông báo hiển thị {match}",
          "severity": "high",
          "test_cases": ["test1", "test2"]
        }
      ],
      "suggested_fix_ref": "REF_TO_CODE_SUGGESTIONS",
      "fix_steps": [
        {
          "step": 1,
          "title": "Tiêu đề bước",
          "explanation": "Giải thích chi tiết"
        }
      ]
    }
  ],
  "test_cases": [...],
  "recommended_learning_path": [...]
}
```

### Chi tiết từng field

| Field | Kiểu | Bắt buộc | Mô tả |
|-------|------|----------|-------|
| `id` | string | ✅ | Định danh duy nhất, format `R_RULE_NAME` |
| `severity` | enum | ✅ | critical/high/medium/low |
| `category` | string | ✅ | Loop Control, Array Access, Recursion, Memory Management |
| `error_type` | string | ✅ | Tên lỗi bằng tiếng Việt |
| `why_it_happens` | string | ✅ | Giải thích nguyên nhân gây lỗi |
| `fix_summary` | string | ✅ | Tóm tắt cách sửa |
| `patterns` | array | ✅ | Mảng các pattern (regex + metadata) |
| `suggested_fix_ref` | string | ❌ | Reference đến code_suggestions.json |
| `fix_steps` | array | ✅ | Các bước sửa chi tiết |

---

## 🔍 Viết Regex Patterns

### Pattern Structure

```json
{
  "regex": "regex_pattern_here",
  "name": "Descriptive name",
  "explanation": "Giải thích regex làm gì",
  "evidence": "Thông báo để hiển thị {match}",
  "severity": "high",
  "test_cases": ["test_input_1", "test_input_2"]
}
```

### Ví dụ Regex Patterns

#### 1️⃣ Infinite Loop Detection

```json
{
  "regex": "while\\s*\\((true|1)\\)\\s*\\{",
  "name": "Infinite while with true/1",
  "explanation": "Phát hiện while(true) hoặc while(1)",
  "evidence": "Vòng lặp vô hạn: {match}",
  "severity": "critical",
  "test_cases": [
    "while(true) {",
    "while (1) {",
    "while ( true ) {",
    "while(1){}"
  ]
}
```

**Breakdown:**
- `while\\s*` - Từ "while" + khoảng trắng tùy ý
- `\\(` - Dấu ngoặc mở (escaped)
- `(true|1)` - Hoặc "true" hoặc "1"
- `\\)` - Dấu ngoặc đóng (escaped)
- `\\s*\\{` - Khoảng trắng + dấu `{`

#### 2️⃣ Off-by-One Loop Detection

```json
{
  "regex": "for\\s*\\([^;]*i\\s*=\\s*0\\s*;\\s*i\\s*<=\\s*n\\s*;",
  "name": "For loop with i<=n",
  "explanation": "for từ 0, nhưng kiểm tra i <= n (sai!)",
  "evidence": "Vòng lặp off-by-one: {match}",
  "severity": "high",
  "test_cases": [
    "for(int i=0; i<=n; i++)",
    "for (int i = 0; i <= n; i++)",
    "for(i=0;i<=n;i++)"
  ]
}
```

**Breakdown:**
- `for\\s*\\(` - "for" + ngoặc mở
- `[^;]*` - Bất cứ ký tự nào trừ `;` (khởi tạo)
- `i\\s*=\\s*0` - `i = 0` với khoảng trắng tùy ý
- `\\s*;\\s*` - Dấu `;` + khoảng trắng
- `i\\s*<=\\s*n\\s*;` - `i <= n` (the problem!)

#### 3️⃣ Uninitialized Array Access

```json
{
  "regex": "int\\s+\\w+\\s*=\\s*a\\[\\s*0\\s*\\]",
  "name": "Variable init from a[0]",
  "explanation": "Khởi tạo từ a[0] mà không check n > 0",
  "evidence": "Khởi tạo không an toàn: {match}",
  "severity": "high",
  "test_cases": [
    "int mx = a[0];",
    "int min = a[ 0 ];",
    "int max=a[0];"
  ]
}
```

**Breakdown:**
- `int\\s+\\w+` - `int` + tên biến
- `\\s*=\\s*` - Dấu `=`
- `a\\[\\s*0\\s*\\]` - `a[0]` với khoảng trắng tùy ý

#### 4️⃣ Recursion Without Base Case

```json
{
  "regex": "(int|long|void)\\s+\\w+\\s*\\([^)]*\\)\\s*\\{[^}]*\\w+\\s*\\(",
  "name": "Recursive call without visible base",
  "explanation": "Hàm gọi chính nó mà không thấy if",
  "evidence": "Hàm đệ quy không có base case: {match}",
  "severity": "critical",
  "test_cases": [
    "int fib(int n) { return fib(n-1)",
    "long fact(int n) { return n * fact(n-1)",
    "void f(int x) { f(x-1); }"
  ]
}
```

**Breakdown:**
- `(int|long|void)\\s+\\w+` - Kiểu trả về + tên hàm
- `\\([^)]*\\)\\s*\\{` - Tham số + dấu `{`
- `[^}]*\\w+\\s*\\(` - Gọi hàm (không check có if trước)

#### 5️⃣ Memory Leak Detection

```json
{
  "regex": "\\bnew\\s+(int|char|float|double|long|short)\\s*\\[",
  "name": "Array allocation with new[]",
  "explanation": "Cấp phát mảng bằng new[] - cần delete[]",
  "evidence": "Cấp phát bộ nhớ: {match}",
  "severity": "high",
  "test_cases": [
    "new int[n]",
    "new char[ size ]",
    "int* a = new int[10];",
    "auto ptr = new double[100];"
  ]
}
```

**Breakdown:**
- `\\b` - Word boundary (bắt đầu từ "new")
- `new\\s+` - "new" + khoảng trắng
- `(int|char|float|...)` - Kiểu dữ liệu
- `\\s*\\[` - Dấu `[` (mảng)

---

## 💡 Ví dụ chi tiết

### Rule hoàn chỉnh: R_OFF_BY_ONE_ARRAY

```json
{
  "id": "R_OFF_BY_ONE_ARRAY",
  "severity": "high",
  "category": "Array Access",
  "error_type": "Sai điều kiện biên mảng (off-by-one)",
  "why_it_happens": "Dùng <= n thay vì < n khi duyệt mảng có n phần tử hoặc không xử lý trường hợp n=0.",
  "fix_summary": "Chỉnh lại điều kiện vòng lặp: [0, n-1] là range hợp lệ cho mảng n phần tử.",
  "patterns": [
    {
      "regex": "for\\s*\\([^;]*i\\s*=\\s*0\\s*;\\s*i\\s*<=\\s*n\\s*;",
      "name": "For loop with i<=n",
      "explanation": "for từ 0, nhưng kiểm tra i <= n truy cập a[n] (ngoài giới hạn)",
      "evidence": "Vòng lặp off-by-one (i<=n): {match}",
      "severity": "high",
      "test_cases": [
        "for(int i=0; i<=n; i++)",
        "for (int i = 0; i <= n; i++)",
        "for(i=0;i<=n;i++)"
      ]
    },
    {
      "regex": "a\\[\\s*n\\s*\\]",
      "name": "Direct access a[n]",
      "explanation": "Truy cập a[n] trực tiếp - ngoài phạm vi [0, n-1]",
      "evidence": "Truy cập mảng ngoài giới hạn: {match}",
      "severity": "high",
      "test_cases": [
        "a[n]",
        "a[ n ]",
        "if (a[n] > x)"
      ]
    }
  ],
  "suggested_fix_ref": "OFF_BY_ONE_LOOP",
  "fix_steps": [
    {
      "step": 1,
      "title": "Hiểu quy tắc chỉ số mảng",
      "explanation": "Mảng n phần tử: [a[0], a[1], ..., a[n-1]]. a[n] là ngoài giới hạn!"
    },
    {
      "step": 2,
      "title": "Sửa điều kiện vòng lặp",
      "explanation": "Thay i <= n bằng i < n trong vòng for."
    },
    {
      "step": 3,
      "title": "Xử lý trường hợp n=0",
      "explanation": "Thêm kiểm tra if (n <= 0) ở đầu hàm."
    }
  ]
}
```

---

## ✅ Best Practices

### 1. Regex Patterns

**✅ GOOD:**
```json
{
  "regex": "for\\s*\\([^;]*i\\s*=\\s*0\\s*;\\s*i\\s*<=\\s*n\\s*;",
  "test_cases": ["for(int i=0; i<=n; i++)", "for(i=0;i<=n;i++)"]
}
```

**❌ BAD:**
```json
{
  "regex": "for.*<=.*n.*;"
}
```
→ Quá generic, sẽ match nhiều code không phải lỗi

### 2. Evidence Messages

**✅ GOOD:**
```
"evidence": "Vòng lặp off-by-one (i<=n): {match}"
```

**❌ BAD:**
```
"evidence": "Pattern found"
```
→ Không cung cấp thông tin cụ thể

### 3. Test Cases

**✅ GOOD:**
```json
"test_cases": [
  "for(int i=0; i<=n; i++)",
  "for (int i = 0; i <= n; i++)",
  "for(i=0;i<=n;i++)"
]
```

**❌ BAD:**
```json
"test_cases": []
```
→ Không có test case để verify regex

### 4. Fix Steps

**✅ GOOD:**
```json
"fix_steps": [
  {
    "step": 1,
    "title": "Hiểu quy tắc chỉ số mảng",
    "explanation": "Mảng n phần tử: a[0]...a[n-1]. a[n] là ngoài giới hạn!"
  },
  {
    "step": 2,
    "title": "Sửa điều kiện",
    "explanation": "Thay i <= n bằng i < n"
  }
]
```

**❌ BAD:**
```json
"fix_steps": [
  {
    "explanation": "Fix the off-by-one error"
  }
]
```
→ Không có cấu trúc, không cụ thể

### 5. Severity Levels

| Level | Khi nào dùng | Ví dụ |
|-------|-------------|-------|
| **critical** | Crash, stack overflow, undefined behavior | Infinite loop, recursion no base case |
| **high** | Runtime error, wrong output | Off-by-one, memory leak |
| **medium** | Logic error, có thể sai | Wrong algorithm, inefficient |
| **low** | Style, không lỗi nhưng có thể cải thiện | Variable naming |

---

## 🧪 Testing Rules

### Cách test regex pattern

```python
import re

# Test pattern
pattern = r"for\s*\([^;]*i\s*=\s*0\s*;\s*i\s*<=\s*n\s*;"
test_cases = [
    "for(int i=0; i<=n; i++)",    # Should match
    "for (int i = 0; i <= n; i++)",  # Should match
    "for(int i=0; i<n; i++)",     # Should NOT match
]

for code in test_cases:
    match = re.search(pattern, code, re.MULTILINE)
    print(f"{'✅' if match else '❌'} {code}")
```

### Cách test cả rule

```bash
# Chạy script validate_rules.py
python backend/validate_rules.py --file rules-refactored.json
```

Output:
```
Validating rules-refactored.json...

R_OFF_BY_ONE_ARRAY
  ✅ Pattern 1: for loop with i<=n
    - Test case 1: ✅ Match
    - Test case 2: ✅ Match
    - Test case 3: ✅ No match (expected)
  
  ✅ Pattern 2: Direct access a[n]
    - Test case 1: ✅ Match

✅ All rules validated!
```

---

## 📝 Checklist để thêm Rule mới

- [ ] Xác định `id` (format: `R_RULE_NAME`)
- [ ] Xác định `severity` (critical/high/medium/low)
- [ ] Xác định `category`
- [ ] Viết `error_type` (tiếng Việt)
- [ ] Viết `why_it_happens` (nguyên nhân)
- [ ] Viết `fix_summary` (tóm tắt sửa)
- [ ] Viết ít nhất 1 regex pattern
  - [ ] Viết `regex` (test cùng lúc)
  - [ ] Viết `name` (mô tả pattern)
  - [ ] Viết `explanation` (giải thích regex làm gì)
  - [ ] Viết `evidence` (thông báo với {match})
  - [ ] Viết `test_cases` (ít nhất 3 case)
- [ ] Thêm code suggestion vào `code_suggestions.json`
- [ ] Viết `fix_steps` (ít nhất 2-3 bước)
- [ ] Test regex bằng Python
- [ ] Run `validate_rules.py` để kiểm tra

---

## 🔗 Reference

### Files liên quan
- [rules-refactored.json](../backend/rules-refactored.json) - Rules chính
- [code_suggestions.json](../backend/code_suggestions.json) - Code suggestions
- [validate_rules.py](../backend/validate_rules.py) - Validation script

### Regex Cheat Sheet
- `\s` - Whitespace
- `\b` - Word boundary
- `[^abc]` - Không phải a, b, c
- `(a|b)` - Hoặc a hoặc b
- `*` - 0 hoặc nhiều lần
- `+` - 1 hoặc nhiều lần
- `?` - 0 hoặc 1 lần
- `{n,m}` - n đến m lần
- `.` - Bất cứ ký tự nào (trừ newline)
- `^` - Đầu dòng
- `$` - Cuối dòng

