class page:

    global_pagecount = 0
    maxcount = 3

    def __init__(self, pageid=None):
        if pageid is None:
            page.global_pagecount += 1
            self.pageid = page.global_pagecount
        else:
            self.pageid = pageid

        self.previouspage = None
        self.registry = {}      # child_pageid -> page
        self.cell = bytearray()
        self.count = 0
        self.tempvalues = []


    # --------------------------------------------------
    # INSERT
    # --------------------------------------------------
    def insert(self, value, otherpagevalue=0):

        # LEAF
        if len(self.registry) == 0:

            self.tempvalues.append(value)
            self.tempvalues.sort()

            if self.count < page.maxcount:

                self._write_record(value, otherpagevalue)
                self.count += 1
                self.sort()

            else:
                self.split_leaf()

        # INTERNAL
        else:
            keys = self.tempvalues
            children = sorted(self.registry.values(),
                              key=lambda c: c.tempvalues[0])

            for i, k in enumerate(keys):
                if value < k:
                    children[i].insert(value)
                    return

            children[-1].insert(value)


    # --------------------------------------------------
    # WRITE RECORD TO CELL
    # --------------------------------------------------
    def _write_record(self, key, childpointer):

        key_bytes = key.to_bytes(2, 'big')

        self.cell.extend(childpointer.to_bytes(2, 'big'))
        self.cell.extend(len(key_bytes).to_bytes(4, 'big'))
        self.cell.extend(key_bytes)


    # --------------------------------------------------
    # BYTE SORT
    # --------------------------------------------------
    def sort(self):

        if self.count <= 1:
            return

        for _ in range(self.count):

            i = 0

            for _ in range(self.count - 1):

                key_len1 = int.from_bytes(self.cell[i+2:i+6], 'big')
                key_start1 = i + 6
                key_end1 = key_start1 + key_len1
                val1 = int.from_bytes(self.cell[key_start1:key_end1], 'big')

                r1_end = key_end1

                j = r1_end

                key_len2 = int.from_bytes(self.cell[j+2:j+6], 'big')
                key_start2 = j + 6
                key_end2 = key_start2 + key_len2
                val2 = int.from_bytes(self.cell[key_start2:key_end2], 'big')

                r2_end = key_end2

                if val1 > val2:
                    rec1 = self.cell[i:r1_end]
                    rec2 = self.cell[j:r2_end]
                    self.cell[i:r2_end] = rec2 + rec1
                else:
                    i = r1_end


    # --------------------------------------------------
    # SPLIT LEAF
    # --------------------------------------------------
    def split_leaf(self):

        keys = self.tempvalues
        mid = len(keys) // 2

        stayer = keys[mid]
        left_keys = keys[:mid]
        right_keys = keys[mid+1:]

        if self.previouspage is None:
            self.breakrootfurther(stayer, left_keys, right_keys)
        else:
            self.mergefurther(stayer, left_keys, right_keys)


    # --------------------------------------------------
    # ROOT SPLIT
    # --------------------------------------------------
    def breakrootfurther(self, promote_key, left_keys, right_keys):

        left_child = page()
        right_child = page()

        left_child.previouspage = self
        right_child.previouspage = self

        # Reset root
        self.cell = bytearray()
        self.registry = {}
        self.tempvalues = [promote_key]
        self.count = 1

        # Write promoted key into root
        self._write_record(promote_key, left_child.pageid)

        self.registry[left_child.pageid] = left_child
        self.registry[right_child.pageid] = right_child

        # Insert keys into children
        for k in left_keys:
            left_child.insert(k)

        for k in right_keys:
            right_child.insert(k)


    # --------------------------------------------------
    # MERGE FURTHER (NON-ROOT SPLIT)
    # --------------------------------------------------
    def mergefurther(self, promote_key, left_keys, right_keys):

        parent = self.previouspage

        # Create new right node
        newnode = page()
        newnode.previouspage = parent

        # Reset current node (becomes left node)
        self.cell = bytearray()
        self.tempvalues = []
        self.count = 0

        for k in left_keys:
            self.insert(k)

        for k in right_keys:
            newnode.insert(k)

        # Insert promoted key into parent
        parent.tempvalues.append(promote_key)
        parent.tempvalues.sort()

        parent._write_record(promote_key, self.pageid)
        parent.count += 1

        parent.registry[newnode.pageid] = newnode

        # Redistribute children if internal node
        if len(self.registry) > 0:

            old_children = list(self.registry.values()) + list(newnode.registry.values())

            self.registry = {}
            newnode.registry = {}

            for child in old_children:
                first_key = child.tempvalues[0]

                if first_key < promote_key:
                    self.registry[child.pageid] = child
                    child.previouspage = self
                else:
                    newnode.registry[child.pageid] = child
                    child.previouspage = newnode

        # If parent overflows → recursive split
        if parent.count > page.maxcount:

            parent_keys = parent.tempvalues
            mid = len(parent_keys) // 2
            promote_up = parent_keys[mid]

            left_keys_parent = parent_keys[:mid]
            right_keys_parent = parent_keys[mid+1:]

            if parent.previouspage is None:
                parent.breakrootfurther(promote_up,
                                        left_keys_parent,
                                        right_keys_parent)
            else:
                parent.mergefurther(promote_up,
                                    left_keys_parent,
                                    right_keys_parent)


    # --------------------------------------------------
    # DISPLAY
    # --------------------------------------------------
    def display(self, level=0):
        print("   " * level + f"Page {self.pageid} -> {self.tempvalues}")
        for child in sorted(self.registry.values(),
                            key=lambda c: c.tempvalues[0]):
            child.display(level+1)
values = [10,20,5,6,12,30,7,17,35,8,9]

root = page()

for v in values:
    root.insert(v)

while root.previouspage:
    root = root.previouspage

root.display()
