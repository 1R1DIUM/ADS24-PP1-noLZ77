import os
from queue import PriorityQueue
from bitarray import bitarray
import pickle

class Huffman:
    class Node():
        def __init__(self,char,freq) -> None:
            self.char = char
            self.freq = freq
            self.left = None
            self.right = None
            
        def __lt__(self,other : 'Huffman.Node'):
            return self.freq < other.freq
    
    def __init__(self) -> None:
        self.huffCodesDict :dict = {}
        self.huffCodesList : list = []
        
    def build_huff_tree(self,alph_and_freq = list[str,int]):
        q = PriorityQueue()
        for char in alph_and_freq:
            node = self.Node(char[0], char[1])
            q.put(node)

        while q.qsize() > 1:
            node1 = q.get()
            node2 = q.get()
            node = self.Node(node1.char + node2.char, node1.freq + node2.freq)
            node.left = node1
            node.right = node2
            q.put(node)
        node = q.get()
        return node
    
    def get_huff_codes(self,node : 'Node', start_code :str = ''):
        if node is None:
            return

        if (node.left is None) and (node.right is None):
            try:
                self.huffCodesList[self.huffCodesList.index(node.char)] = start_code
            except ValueError:
                self.huffCodesList.append([node.char,start_code])
            
        self.get_huff_codes(node.left, start_code + "0")
        self.get_huff_codes(node.right, start_code + "1")
        
    def getSorted_alph_freq(self,in_str :str):
        afList = []
        set_alphabet = sorted(set(in_str))
        for symbol in set_alphabet:
            curr_amount = in_str.count(symbol)
            afList.append((symbol,curr_amount))
        return sorted(afList, key= lambda x:[(x[1],x[0])])
    
    def toCanonicalHuffCodes(self):
        self.huffCodesList[0][1] = '0'*len(self.huffCodesList[0][1])
        for i in range(1, len(self.huffCodesList)):
            oldlen = len(self.huffCodesList[i][1]) 
            dif_len = len(self.huffCodesList[i][1]) - len(self.huffCodesList[i-1][1])
            self.huffCodesList[i][1] = bin(int(self.huffCodesList[i-1][1],2)+1)[2:].zfill(oldlen-dif_len) 
            
            while len(self.huffCodesList[i][1]) < oldlen:
                self.huffCodesList[i][1] +='0'
    
    def bit_str_to_chars(self,bit_str):

        out_lst =[]
        last_len = 0
        for i in range(0,len(bit_str),8):
            slice = bit_str[i:i+8]
            if len(slice) < 8:
                last_len = len(slice)
            out_lst.append(chr(int(bit_str[i:i+8],2)))
        str =  "".join(out_lst)
        
    
        return str,last_len
    
    def bit_str_to_bytes(self,bit_str):
        out_lst = []
        last_len = 0
        for i in range(0,len(bit_str),8):
            slice = bit_str[i:i+8]
            if len(slice) < 8:
                last_len = len(slice)
            out_lst.append((int(bit_str[i:i+8],2)))
        ba = bytearray(out_lst)
        
        return ba,last_len
        
    def sort_huff_code(self):
        self.huffCodesList.sort(key = lambda x:[[len(x[1]),x[0]]])
    
    def encode(self, in_str,alph_freq_list : list): 
        node = self.build_huff_tree(alph_freq_list)
        self.get_huff_codes(node)
        self.sort_huff_code()
        self.toCanonicalHuffCodes()

        for chr_ind in range(len(self.huffCodesList)):
            self.huffCodesDict[self.huffCodesList[chr_ind][0]] = bitarray(self.huffCodesList[chr_ind][1])
        
        encoded = bitarray()
        bitarray.encode(encoded,self.huffCodesDict,in_str)
        
        encoded_str,last_len = self.bit_str_to_bytes(encoded.to01())
        
        return encoded_str,last_len 
    
    def encode_file(self,in_filename_format,out_filename_format):
        with open(in_filename_format,'r',encoding='utf-8') as read_f:
            
            in_str = read_f.read()
            
            alph_freq_list = self.getSorted_alph_freq(in_str)
            byte_str,last_len = self.encode(in_str,alph_freq_list)
            
            
            with open(out_filename_format,'wb')as write_f:
                pickle.dump(self.huffCodesDict,write_f)
            
                write_f.write(b'\n')
                write_f.write(byte_str)
                
                last = bytearray()
                last.append(last_len)
                write_f.write(bytearray(last))
    
    def encode_file_bin(self,in_filename_format,out_filename_format):
        with open(in_filename_format,'rb') as read_f:
            
            bin_str = read_f.read()
            in_lst = []
            
            for byte in bin_str:
                in_lst.append(chr(byte))
            in_str = "".join(in_lst)

            alph_freq_list = self.getSorted_alph_freq(in_str)
            byte_str,last_len = self.encode(in_str,alph_freq_list)
            
            
            with open(out_filename_format,'wb')as write_f:
                pickle.dump(self.huffCodesDict,write_f)
            
                write_f.write(b'\n')
                write_f.write(byte_str)
                
                last = bytearray()
                last.append(last_len)
                write_f.write(bytearray(last))
    
    def decode_file_bin(self,in_filename_format,out_filename_format):
        with open(in_filename_format, 'rb') as read_f:
            huff_dict = pickle.load(read_f)

            read_f.readline()
            encoded_text_pos = read_f.tell()
            
            with open(out_filename_format,'wb') as write_f:
                read_f.seek(0,2) #? to end of file
                file_size = read_f.tell() -encoded_text_pos - 1
                
                read_f.seek(-1,2)
                last_len = int.from_bytes(read_f.read(1))
                read_f.seek(encoded_text_pos)
                
                bit_lst = []
                encoded_data = read_f.read()
                for symbol_ind in range(len(encoded_data)-1):
                    symbol = encoded_data[symbol_ind]
                    bit_symbol = bin(symbol)[2:]
                    if symbol_ind == len(encoded_data)-2:   
                        bit_symbol = bit_symbol.zfill(last_len)
                    else:
                        bit_symbol = bit_symbol.zfill(8)
                    bit_lst.append(bit_symbol)
                
                
                encoded_bit_str = "".join(bit_lst)
                decoded_bit_str = bitarray(encoded_bit_str)
                decoded_list = decoded_bit_str.decode(huff_dict)
                decoded_str = "".join(decoded_list)
                
                decoded_bin_lst = bytearray()
                for char in decoded_str:
                    decoded_bin_lst.append(ord(char))
                
                write_f.write(decoded_bin_lst)
    
    def decode_file(self,in_filename_format,out_filename_format):
        with open(in_filename_format, 'rb') as read_f:
            huff_dict = pickle.load(read_f)
        
            
            read_f.readline()
            encoded_text_pos = read_f.tell()
            with open(out_filename_format,'w',encoding='utf-8',newline='\x0A') as write_f:
                read_f.seek(0,2) #? to end of file

                
                read_f.seek(-1,2)
                last_len = int.from_bytes(read_f.read(1))
                read_f.seek(encoded_text_pos)
                
                bit_lst = []
                encoded_data = read_f.read()
                for symbol_ind in range(len(encoded_data)-1):
                    symbol = encoded_data[symbol_ind]
                    bit_symbol = bin(symbol)[2:]
                    if symbol_ind == len(encoded_data)-2:   
                        bit_symbol = bit_symbol.zfill(last_len)
                    else:
                        bit_symbol = bit_symbol.zfill(8)
                    bit_lst.append(bit_symbol)
                
                
                encoded_bit_str = "".join(bit_lst)
                decoded_bit_str = bitarray(encoded_bit_str)
                decoded_list = decoded_bit_str.decode(huff_dict)
                decoded_str = "".join(decoded_list)
                write_f.write(decoded_str.replace('\n','\x0A'))

        return
                
huffma = Huffman()
#huffma.encode_file("war_and_peace.ru.txt","outwar.txt")
#huffma.decode_file("outwar.txt","war_test.txt")

code_file = r"wik8_com.txt"
com_file = r"wb_LZ77_HA_com.txt"
decom_file = r"wb_LZ77_decom.txt"

huffma.encode_file_bin(code_file,com_file)
huffma.decode_file_bin(com_file,decom_file)


with open(code_file,'rb') as file1:
    str1 = file1.read()
with open(decom_file,'rb') as file2:
    str2 = file2.read()
    
print(str1==str2)