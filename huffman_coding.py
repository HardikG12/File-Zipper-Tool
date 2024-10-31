import os
import heapq

class HuffmanCoding:
    def __init__(self, path):
        self.path = path
        self.heap = []
        self.codes = {}
        self.reverse_map = {}

    class HeapNode:
        def __init__(self, char, freq):
            self.char = char
            self.freq = freq
            self.left = None
            self.right = None

        def __lt__(self, other):
            return self.freq < other.freq
        
        def __eq__(self, other):
            if other is None:
                return False
            if not isinstance(other, self.HeapNode):
                return False
            return self.freq == other.freq
        
    def freq_dict(self, text):
        # Calculate the frequency of each character in the text
        freq = {}
        for cha in text:
            if cha not in freq:
                freq[cha] = 0
            freq[cha] += 1
        return freq

    def make_heap(self, frequency):
        for key in frequency:
            node = self.HeapNode(key, frequency[key])
            heapq.heappush(self.heap, node)

    def merge_codes(self):
        while len(self.heap) > 1:
            node1 = heapq.heappop(self.heap)
            node2 = heapq.heappop(self.heap)

            merged = self.HeapNode(None, node1.freq + node2.freq)
            merged.left = node1
            merged.right = node2
            heapq.heappush(self.heap, merged)

    def make_codes_helper(self, node, curr):
        if node is None:
            return 
        if node.char is not None:
            self.codes[node.char] = curr
            self.reverse_map[curr] = node.char
        self.make_codes_helper(node.left, curr + "0")
        self.make_codes_helper(node.right, curr + "1")

    def make_codes(self):
        root = heapq.heappop(self.heap)
        curr = ""
        heapq.heappush(self.heap, root)
        self.make_codes_helper(root, curr)

    def get_encoded_text(self, text):
        encoded_text = []
        for char in text:
            encoded_text.append(self.codes[char])
        return ''.join(encoded_text)

    def pad_encoded_text(self, encoded_text):
        extra_padding = 8 - len(encoded_text) % 8
        # Add extra padding zeros
        for i in range(extra_padding):
            encoded_text += "0"
        padded_info = "{0:08b}".format(extra_padding)
        encoded_text = padded_info + encoded_text
        return encoded_text

    def get_byte_array(self, padded_encoded_text):
        b = bytearray()
        for i in range(0, len(padded_encoded_text), 8):
            byte = padded_encoded_text[i:i + 8]
            b.append(int(byte, 2))
        return b

    def compress(self):
        filename, file_extension = os.path.splitext(self.path)
        output_path = filename + ".bin"
        with open(self.path, 'r') as file, open(output_path, 'wb') as out:
            text = file.read()
            text = text.rstrip()

            frequency = self.freq_dict(text)
            self.make_heap(frequency)
            self.merge_codes()
            self.make_codes()

            encoded_text = self.get_encoded_text(text)
            padded_encoded_text = self.pad_encoded_text(encoded_text)
            b = self.get_byte_array(padded_encoded_text)
            out.write(bytes(b))

        print("Compressed")
        return output_path
    
    def decode_text(self, encoded_text):
        curr = ""
        dec = ""

        for bit in encoded_text:
            curr += bit
            if curr in self.reverse_map:
                char = self.reverse_map[curr]
                dec += char
                curr = ""

        return dec

    def remove_padding(self, bit_string):
        padded_info = bit_string[:8]
        extra_padding = int(padded_info, 2)
        # Correct the slicing of the bit_string
        bit_string = bit_string[8:]  # Start from index 8
        encoded_text = bit_string[:-extra_padding]  # Remove the extra padding
        return encoded_text

    def decompress(self, input_path):
        filename, file_extension = os.path.splitext(input_path)
        output_path = filename + "_decompressed" + ".txt"

        with open(input_path, 'rb') as file, open(output_path, 'w') as output:
            bit_string = ""
            byte = file.read(1)
            while len(byte) > 0:
                byte = ord(byte)  # Convert byte to an integer
                bits = bin(byte)[2:].rjust(8, '0')  # Ensure we get 8 bits
                bit_string += bits
                byte = file.read(1)

            encoded_string = self.remove_padding(bit_string)
            decoded_text = self.decode_text(encoded_string)

            output.write(decoded_text)
        
        print("Decompressed")
        return output_path
    
