import pickle
from queue import PriorityQueue
from bitarray import bitarray
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

class BWT_MTF_HA:
    
    def encode_file(self,in_filename_format,out_filename_format,BWT_DELIM:str):
        with open(in_filename_format,'r',encoding='utf-8',newline='\x0A') as read_f:
            HUFFMAN_CLASS = Huffman()
            uni_mtf_list, data_list = BWT_MTF.encode(read_f.read(),BWT_DELIM)
  
            alph_freq_list = HUFFMAN_CLASS.getSorted_alph_freq("".join(uni_mtf_list))
            encoded_huf,last_len = HUFFMAN_CLASS.encode("".join(uni_mtf_list),alph_freq_list)

            data_list.append(last_len)
            data_list.append(HUFFMAN_CLASS.huffCodesDict)
            data_list.append(encoded_huf)
            
            with open(out_filename_format,'wb') as write_f:
                pickle.dump(data_list,write_f)
    
    def decode_Huf(self,encoded_data,last_len,huff_dict):
        bit_lst = []

        for symbol_ind in range(len(encoded_data)):
            symbol = encoded_data[symbol_ind]
            bit_symbol = bin(symbol)[2:]
            if symbol_ind == len(encoded_data)-1:   
                bit_symbol = bit_symbol.zfill(last_len)
            else:
                bit_symbol = bit_symbol.zfill(8)
            bit_lst.append(bit_symbol)
        
        
        encoded_bit_str = "".join(bit_lst)
        decoded_bit_str = bitarray(encoded_bit_str)
        decoded_list = decoded_bit_str.decode(huff_dict)
        decoded_str = "".join(decoded_list)
        return decoded_str
    
    def decode_file(self,in_filename_format,out_filename_format):
        with open (in_filename_format,'rb') as read_f:
            data_list = pickle.load(read_f)
            BWT_index,MTF_alphabet,HUF_last_len,huf_dict,encoded_huf = data_list
            
            after_huf_str = self.decode_Huf(encoded_huf,HUF_last_len,huf_dict)
            after_bwt_str = BWT_MTF.decode(after_huf_str,BWT_index,MTF_alphabet)
            
            
            with open(out_filename_format,'w',encoding='utf-8',newline='\x0A') as write_f:
                write_f.write(after_bwt_str)
    
    
    def encode_file_bin(self,in_filename_format,out_filename_format,BWT_DELIM:str):
        with open(in_filename_format,'rb') as read_f:
            bin_str = read_f.read()
            in_str = IMAGE_METHODS.img_to_str(bin_str)
            HUFFMAN_CLASS = Huffman()
            uni_mtf_list, data_list = BWT_MTF.encode(in_str,BWT_DELIM)
            
            alph_freq_list = HUFFMAN_CLASS.getSorted_alph_freq("".join(uni_mtf_list))
            encoded_huf,last_len = HUFFMAN_CLASS.encode("".join(uni_mtf_list),alph_freq_list)
            data_list.append(last_len)
            data_list.append(HUFFMAN_CLASS.huffCodesDict)
            data_list.append(encoded_huf)
            with open(out_filename_format,'wb') as write_f:
                pickle.dump(data_list,write_f)

    def decode_file_bin(self,in_filename_format,out_filename_format):
        with open (in_filename_format,'rb') as read_f:
            data_list = pickle.load(read_f)
            BWT_index,MTF_alphabet,HUF_last_len,huf_dict,encoded_huf = data_list
            after_huf_str = self.decode_Huf(encoded_huf,HUF_last_len,huf_dict)
            after_bwt_str = BWT_MTF.decode(after_huf_str,BWT_index,MTF_alphabet)
            
            ba = IMAGE_METHODS.str_to_byteArray(after_bwt_str)
            with open(out_filename_format,'wb') as write_f:
                write_f.write(ba)

            
class IMAGE_METHODS:
    @staticmethod
    def img_to_str(bin_str):
        in_lst = []
        for byte in bin_str:
            in_lst.append(chr(byte))    

        in_str = "".join(in_lst)
        return in_str
    @staticmethod
    def str_to_byteArray(in_str):
        decoded_bin_lst = bytearray()
        for char in in_str:
            decoded_bin_lst.append(ord(char))
        return decoded_bin_lst

import sufarray
class BWT:
    def __init__(self) -> None:
        self.encoded_str = ''

    def encode(self,in_str):
        sArray = sufarray.SufArray(in_str)
        suffix_array = sArray.get_array()
        index = suffix_array.index(0)
        encoded_data = []
        for j in suffix_array:
            i = j-1
            if i < 0:
                i += len(suffix_array)
            encoded_data.append(in_str[i])
        return index, "".join(encoded_data)
    
    def decode(self,index, encoded_str) -> str:

        shifts = [(encoded_str[i],i) for i in range(len(encoded_str))]
        shifts.sort()
        new_indixes = list(zip(*shifts))[1]
        decoded = []
        ind = index
        for _ in range(len(encoded_str)-1):
            ind = new_indixes[ind]
            decoded.append(encoded_str[ind])
        return "".join(decoded)

class MTF:
     
    def encode(self,in_str:str,alphabet:list):
        out_lst = []
        alph = alphabet[:]
        for char in in_str:
            index = alph.index(char)
            out_lst.append(index)
            alph.remove(char)
            alph.insert(0,char)
        return out_lst


    def decode(self,in_str:str, alphabet :list)-> str:
        out_list = []
        out_alphabet = alphabet
        
        for num in in_str:
            char = out_alphabet[ord(num)]
            out_list.append(char)
            out_alphabet.remove(char)
            out_alphabet.insert(0,char)
        
        return "".join(out_list)



class BWT_MTF:
    @staticmethod
    def encode(in_str,BWT_DELIM):
        '''$ added auto. Returns unicode list and data list [BWT_index,MTF_alphabet]'''
        bwt = BWT()
        index,bwt_string = bwt.encode(in_str+BWT_DELIM)
        mtf = MTF()
        HUFFMAN_CLASS = Huffman()
        
        
        alph = []
        alph_freq_list = HUFFMAN_CLASS.getSorted_alph_freq(bwt_string)
        for eleme in alph_freq_list:
            alph.append(eleme[0])
        
        alph.reverse()
        mtf_lst = mtf.encode(bwt_string,alph)
        
        uni_mtf_list = []
        for num in mtf_lst:
            uni_mtf_list.append(chr(num))
            
        data_list = [index,alph]   #!DATA LIST
        return uni_mtf_list,data_list

    @staticmethod
    def decode(encoded_str, BWT_index,MTF_alphabet):
        mtf = MTF()
        after_mtf_str = mtf.decode(encoded_str,MTF_alphabet)
        
        bwt = BWT()
        after_bwt_str = bwt.decode(BWT_index,after_mtf_str)
        return after_bwt_str


    @staticmethod
    def get_unique_symbol(in_str : str):
        for i in range(0,int('0x10ffff',16)):
            if chr(i) not in in_str:
                return chr(i)
def main_BWT_MTF_HA():
    
    #*
    code_file = "war_and_peace.ru.txt"
    com_file ="war_and_peace_com.txt"
    decom_file = "war_and_peace.ru_decom.txt"


    bmh = BWT_MTF_HA()
    bmh.encode_file(code_file,com_file,'\x10')
    bmh.decode_file(com_file,decom_file)


    with open(code_file,'r',encoding='utf-8',newline='\x0A') as file1:
            str1 = file1.read()
    with open(decom_file,'r',encoding='utf-8',newline='\x0A') as file2:
            str2 = file2.read()
            
    print(str1==str2)
    
  
    

if __name__ == '__main__':
    main_BWT_MTF_HA()