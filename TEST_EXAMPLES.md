# Test Examples từ rules.json

Dưới đây là các ví dụ code để test hệ thống chẩn đoán lỗi logic/thuật toán.

---

## 1️⃣ R_INFINITE_LOOP_WHILE - Vòng lặp vô hạn

### ❌ Code có lỗi: While(true)
```cpp
#include <iostream>
using namespace std;

int main() {
  int n;
  cin >> n;
  int i = 0;
  
  while (true) {
    cout << i << " ";
    // Quên tăng i hoặc thiếu điều kiện dừng
  }
  
  return 0;
}
```

**Lỗi phát hiện:** Vòng lặp vô hạn - `while (true)`
**Giải thích:** Điều kiện vô điều kiện là `true` nên vòng lặp sẽ chạy mãi.

---

### ✅ Code sửa lại
```cpp
#include <iostream>
using namespace std;

int main() {
  int n;
  cin >> n;
  
  for (int i = 0; i < n; i++) {
    cout << i << " ";
  }
  
  return 0;
}
```

---

## 2️⃣ R_OFF_BY_ONE_ARRAY - Sai điều kiện biên mảng

### ❌ Code có lỗi: i <= n thay vì i < n
```cpp
#include <iostream>
using namespace std;

int main() {
  int n;
  cin >> n;
  
  int a[1000];
  
  // Sai: duyệt đến i <= n, sẽ truy cập a[n] (ngoài giới hạn)
  for (int i = 0; i <= n; i++) {
    cin >> a[i];
  }
  
  // Tìm max
  int mx = a[0];
  for (int i = 1; i <= n; i++) {
    if (a[i] > mx) mx = a[i];
  }
  
  cout << mx << endl;
  
  return 0;
}
```

**Lỗi phát hiện:** Off-by-one - `for (int i = 0; i <= n; i++)`
**Giải thích:** Mảng có n phần tử, chỉ số hợp lệ là [0, n-1]. Truy cập a[n] là truy cập ngoài giới hạn!

---

### ✅ Code sửa lại
```cpp
#include <iostream>
using namespace std;

int main() {
  int n;
  cin >> n;
  
  // Kiểm tra n > 0
  if (n <= 0) {
    cout << "Lỗi: n phải > 0" << endl;
    return 1;
  }
  
  int a[1000];
  
  // Đúng: duyệt đến i < n
  for (int i = 0; i < n; i++) {
    cin >> a[i];
  }
  
  // Tìm max
  int mx = a[0];
  for (int i = 1; i < n; i++) {
    if (a[i] > mx) mx = a[i];
  }
  
  cout << mx << endl;
  
  return 0;
}
```

---

## 3️⃣ R_UNINITIALIZED_ARRAY_ACCESS - Truy cập mảng không khởi tạo

### ❌ Code có lỗi: Khởi tạo mx từ a[0] mà không kiểm tra n > 0
```cpp
#include <iostream>
using namespace std;

int main() {
  int n;
  cin >> n;
  
  int a[1000];
  for (int i = 0; i < n; i++) {
    cin >> a[i];
  }
  
  // Sai: nếu n = 0, a[0] là truy cập không hợp lệ
  int mx = a[0];
  for (int i = 1; i < n; i++) {
    if (a[i] > mx) mx = a[i];
  }
  
  cout << mx << endl;
  
  return 0;
}
```

**Lỗi phát hiện:** Truy cập mảng không khởi tạo - `int mx = a[0]`
**Giải thích:** Nếu n=0, không có phần tử trong mảng, truy cập a[0] gây lỗi.

---

### ✅ Code sửa lại - Cách 1: Kiểm tra n > 0
```cpp
#include <iostream>
#include <climits>
using namespace std;

int main() {
  int n;
  cin >> n;
  
  if (n <= 0) {
    cout << "Lỗi: n phải > 0" << endl;
    return 1;
  }
  
  int a[1000];
  for (int i = 0; i < n; i++) {
    cin >> a[i];
  }
  
  int mx = a[0];
  for (int i = 1; i < n; i++) {
    if (a[i] > mx) mx = a[i];
  }
  
  cout << mx << endl;
  
  return 0;
}
```

### ✅ Code sửa lại - Cách 2: Dùng INT_MIN
```cpp
#include <iostream>
#include <climits>
using namespace std;

int main() {
  int n;
  cin >> n;
  
  int a[1000];
  for (int i = 0; i < n; i++) {
    cin >> a[i];
  }
  
  // Đúng: khởi tạo với INT_MIN
  int mx = INT_MIN;
  for (int i = 0; i < n; i++) {
    if (a[i] > mx) mx = a[i];
  }
  
  // Kiểm tra kết quả
  if (mx == INT_MIN) {
    cout << "Không có phần tử" << endl;
  } else {
    cout << mx << endl;
  }
  
  return 0;
}
```

---

## 4️⃣ R_RECURSION_NO_BASE_CASE - Đệ quy thiếu điểm dừng

### ❌ Code có lỗi: Thiếu base case
```cpp
#include <iostream>
using namespace std;

// Thiếu base case
int factorial(int n) {
  return n * factorial(n - 1);  // Sẽ gọi mãi, không dừng
}

int main() {
  int n;
  cin >> n;
  cout << factorial(n) << endl;
  return 0;
}
```

**Lỗi phát hiện:** Đệ quy thiếu điểm dừng
**Giải thích:** Hàm `factorial` gọi lại chính nó mà không có điều kiện dừng, dẫn đến tràn ngăn xếp (stack overflow).

---

### ✅ Code sửa lại
```cpp
#include <iostream>
using namespace std;

int factorial(int n) {
  // Base case: n = 0 hoặc n = 1
  if (n <= 1) {
    return 1;
  }
  
  // Recursive case: n > 1
  return n * factorial(n - 1);
}

int main() {
  int n;
  cin >> n;
  
  if (n < 0) {
    cout << "Lỗi: n >= 0" << endl;
    return 1;
  }
  
  cout << factorial(n) << endl;
  return 0;
}
```

---

### ❌ Thêm ví dụ: Đệ quy Fibonacci thiếu base case
```cpp
#include <iostream>
using namespace std;

int fibonacci(int n) {
  // Thiếu base case, chỉ có recursive case
  return fibonacci(n - 1) + fibonacci(n - 2);
}

int main() {
  cout << fibonacci(5) << endl;
  return 0;
}
```

### ✅ Sửa: Fibonacci với base case
```cpp
#include <iostream>
using namespace std;

int fibonacci(int n) {
  // Base cases
  if (n == 0) return 0;
  if (n == 1) return 1;
  
  // Recursive case
  return fibonacci(n - 1) + fibonacci(n - 2);
}

int main() {
  cout << fibonacci(5) << endl;  // Output: 5
  return 0;
}
```

---

## 5️⃣ R_MEMORY_LEAK_NEW - Rò rỉ bộ nhớ với new

### ❌ Code có lỗi: Cấp phát với new nhưng không giải phóng
```cpp
#include <iostream>
using namespace std;

int main() {
  int n;
  cin >> n;
  
  // Cấp phát mảng động
  int* a = new int[n];
  
  for (int i = 0; i < n; i++) {
    cin >> a[i];
  }
  
  // Tìm max
  int mx = a[0];
  for (int i = 1; i < n; i++) {
    if (a[i] > mx) mx = a[i];
  }
  
  cout << mx << endl;
  
  // Quên giải phóng bộ nhớ - RÒ RỈ BỘ NHỚ!
  // delete[] a;
  
  return 0;
}
```

**Lỗi phát hiện:** Rò rỉ bộ nhớ - `int* a = new int[n]`
**Giải thích:** Cấp phát bộ nhớ bằng `new` nhưng không giải phóng bằng `delete[]`. Bộ nhớ sẽ không được trả lại cho hệ thống, gây rò rỉ.

---

### ✅ Code sửa lại - Cách 1: Dùng delete[]
```cpp
#include <iostream>
using namespace std;

int main() {
  int n;
  cin >> n;
  
  int* a = new int[n];
  
  for (int i = 0; i < n; i++) {
    cin >> a[i];
  }
  
  int mx = a[0];
  for (int i = 1; i < n; i++) {
    if (a[i] > mx) mx = a[i];
  }
  
  cout << mx << endl;
  
  // Giải phóng bộ nhớ đúng cách
  delete[] a;
  a = nullptr;  // Đặt nullptr để tránh use-after-free
  
  return 0;
}
```

### ✅ Code sửa lại - Cách 2: Dùng std::vector (AN TOÀN NHẤT)
```cpp
#include <iostream>
#include <vector>
using namespace std;

int main() {
  int n;
  cin >> n;
  
  // Dùng vector thay vì new - tự động quản lý bộ nhớ
  vector<int> a(n);
  
  for (int i = 0; i < n; i++) {
    cin >> a[i];
  }
  
  int mx = a[0];
  for (int i = 1; i < n; i++) {
    if (a[i] > mx) mx = a[i];
  }
  
  cout << mx << endl;
  
  // Không cần delete - vector tự động giải phóng khi ra khỏi scope
  
  return 0;
}
```

---

## 📝 Bảng tóm tắt Test Cases

| Rule ID | Lỗi | Ví dụ Code | Test Case | Kỳ vọng |
|---------|-----|-----------|-----------|---------|
| R_INFINITE_LOOP_WHILE | while(true) | while(true) { } | Bất kỳ | Phát hiện vòng lặp vô hạn |
| R_OFF_BY_ONE_ARRAY | i <= n | for(i=0; i<=n; i++) a[i] | n=5 | Phát hiện off-by-one |
| R_UNINITIALIZED_ARRAY_ACCESS | a[0] không check | int mx = a[0]; (n có thể 0) | n=0 | Phát hiện truy cập không hợp lệ |
| R_RECURSION_NO_BASE_CASE | Thiếu if return | factorial(n) { return n*factorial(n-1); } | n=5 | Phát hiện thiếu base case |
| R_MEMORY_LEAK_NEW | Không delete[] | int* a = new int[n]; (không delete) | Bất kỳ | Phát hiện rò rỉ bộ nhớ |

---

## 🚀 Cách test trên hệ thống

1. Copy từng code example ở trên
2. Dán vào **"Mã nguồn sinh viên (C/C++)"** trên web
3. Chọn ngôn ngữ **C++**
4. Bấm **"Phân tích mã nguồn"**
5. Kiểm tra kết quả:
   - ✅ Có hiển thị lỗi tương ứng?
   - ✅ Có hiển thị các bước sửa?
   - ✅ Có gợi ý test case?

---

## 📊 Test Matrix - Các trường hợp biên

### Bài: Tìm max trong mảng

```
Test Case 1: n=0 (Biên dưới)
Input: n = 0
Mục đích: Kiểm tra lỗi off-by-one và uninitialized access
Kỳ vọng: Phát hiện R_UNINITIALIZED_ARRAY_ACCESS

Test Case 2: n=1 (Biên nhỏ)
Input: n = 1, a = [5]
Mục đích: Kiểm tra vòng lặp chỉ 1 lần
Kỳ vọng: Không lỗi nếu code đúng

Test Case 3: n=3, số âm
Input: n = 3, a = [-5, -2, -10]
Mục đích: Kiểm tra khởi tạo max = INT_MIN
Kỳ vọng: Kết quả đúng -2

Test Case 4: n=1000 (Biên lớn)
Input: n = 1000
Mục đích: Kiểm tra tràn bộ đệm a[1000]
Kỳ vọng: Phát hiện nếu dùng a[1000]
```

### Bài: Giai thừa đệ quy

```
Test Case 1: n=5 (Bình thường)
Input: n = 5
Kỳ vọng: Output 120

Test Case 2: n=0 (Base case)
Input: n = 0
Kỳ vọng: Output 1

Test Case 3: n=-1 (Số âm)
Input: n = -1
Kỳ vọng: Phát hiện đệ quy vô hạn nếu thiếu check
```

---

## 💡 Hướng dẫn viết test code của riêng bạn

Để test toàn diện, bạn nên viết code có:

1. ✅ **Code đúng** - Không lỗi, để kiểm tra false positive
2. ❌ **Code sai từng loại** - Từng loại lỗi một cái
3. 🎯 **Test case biên** - n=0, n=1, n=max
4. 🔍 **Test case bình thường** - Giá trị đơn giản
5. 🚨 **Test case cực trị** - Số âm, số lớn, v.v.

---

## 📌 Lưu ý quan trọng

- Code test nên **biên dịch được** để tránh lỗi syntax
- Nên test từng lỗi một để rõ hệ thống phát hiện nào
- Nếu không phát hiện được, kiểm tra regex pattern trong rules.json
- Có thể test cả code **đúng** để đảm bảo không có false positive

