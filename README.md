# Byte-Level Page-Based B-Tree (From Scratch)

This project implements a B-Tree from scratch in Python using **byte-level page storage**, inspired by how real database storage engines manage index pages internally.

Unlike typical textbook B-Tree implementations that store keys in lists or arrays, this implementation:

- Stores records inside a `bytearray`
- Manually manages key offsets and lengths
- Encodes child pointers in bytes
- Performs record swapping at the byte level
- Implements bottom-up split propagation
- Redistributes children during internal node splits

This is closer to how database engines handle page-structured indexes.

---

##Key Features

- Order-3 B-Tree (max 3 keys per page)
- Byte-level record layout
- Manual offset calculation
- Byte-level bubble sort for record ordering
- Leaf and internal node splitting
- Parent pointer maintenance
- Bottom-up recursive split propagation
- Child redistribution based on key comparison

---

##  Page Layout Design

Each record inside a page is stored as:
[2 bytes child_page_id]
[4 bytes key_length]
[key_length bytes key]
Record size:


6 + key_length bytes


---This simulates how a database engine might store keys inside a fixed-size page.---
## 🔧 Example Usage


values = [10,20,5,6,12,30,7,17,35,8,9]

root = page()

for v in values:
    root.insert(v)

while root.previouspage:
    root = root.previouspage

root.display()

Sample Output

Page 1 -> [7, 10, 20]
   Page 2 -> [5, 6]
   Page 5 -> [8, 9]
   Page 3 -> [12, 17]
   Page 4 -> [30, 35]
