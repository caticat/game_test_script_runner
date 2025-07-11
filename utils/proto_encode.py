import struct
import math
from typing import List, Tuple, Dict, Union


class Codec:
    @staticmethod
    def encode_bool(value: bool) -> bytes:
        return bytes([1 if value else 0])

    @staticmethod
    def encode_int8(value: int) -> bytes:
        return struct.pack('<b', value)

    @staticmethod
    def encode_uint8(value: int) -> bytes:
        return struct.pack('<B', value)

    @staticmethod
    def encode_varint(value: int) -> bytes:
        result = bytearray()
        while value >= 0x80:
            result.append((value & 0x7F) | 0x80)
            value >>= 7
        result.append(value)
        return bytes(result)

    @staticmethod
    def encode_int16(value: int) -> bytes:
        return Codec.encode_varint(value & 0xFFFF)

    @staticmethod
    def encode_uint16(value: int) -> bytes:
        return Codec.encode_varint(value)

    @staticmethod
    def encode_int32(value: int) -> bytes:
        return Codec.encode_varint(value & 0xFFFFFFFF)

    @staticmethod
    def encode_uint32(value: int) -> bytes:
        return Codec.encode_varint(value)

    @staticmethod
    def encode_int64(value: int) -> bytes:
        return Codec.encode_varint(value & 0xFFFFFFFFFFFFFFFF)

    @staticmethod
    def encode_uint64(value: int) -> bytes:
        return Codec.encode_varint(value)

    @staticmethod
    def encode_string(value: str) -> bytes:
        encoded = value.encode('utf-8')
        return Codec.encode_varint(len(encoded)) + encoded

    @staticmethod
    def encode_bytes(value: bytes) -> bytes:
        return Codec.encode_int32(len(value)) + value

    @staticmethod
    def encode_float32(value: float) -> bytes:
        return struct.pack('<f', value)

    @staticmethod
    def encode_int32_list(values: List[int]) -> bytes:
        out = Codec.encode_int32(len(values))
        for v in values:
            out += Codec.encode_int32(v)
        return out

    @staticmethod
    def encode_int64_list(values: List[int]) -> bytes:
        out = Codec.encode_int32(len(values))
        for v in values:
            out += Codec.encode_int64(v)
        return out

    @staticmethod
    def decode_varint(buff: bytes, pos: int) -> Tuple[int, int]:
        shift = 0
        result = 0
        while True:
            if pos >= len(buff):
                raise ValueError('decode buffer not enough')
            b = buff[pos]
            pos += 1
            result |= ((b & 0x7F) << shift)
            if (b & 0x80) == 0:
                break
            shift += 7
        return result, pos

    @staticmethod
    def decode_bool(buff: bytes, pos: int) -> Tuple[bool, int]:
        if pos >= len(buff):
            raise ValueError('decode buffer not enough')
        return buff[pos] != 0, pos + 1

    @staticmethod
    def decode_uint8(buff: bytes, pos: int) -> Tuple[int, int]:
        if pos >= len(buff):
            raise ValueError('decode buffer not enough')
        return buff[pos], pos + 1
    
    @staticmethod
    def decode_int16(buff: bytes, pos: int) -> Tuple[int, int]:
        val, pos = Codec.decode_varint(buff, pos)
        return int(val), pos

    @staticmethod
    def decode_int32(buff: bytes, pos: int) -> Tuple[int, int]:
        val, pos = Codec.decode_varint(buff, pos)
        return int(val), pos

    @staticmethod
    def decode_int64(buff: bytes, pos: int) -> Tuple[int, int]:
        val, pos = Codec.decode_varint(buff, pos)
        return int(val), pos

    @staticmethod
    def decode_float32(buff: bytes, pos: int) -> Tuple[float, int]:
        if pos + 4 > len(buff):
            raise ValueError('decode buffer not enough')
        return struct.unpack('<f', buff[pos:pos+4])[0], pos + 4

    @staticmethod
    def decode_string(buff: bytes, pos: int) -> Tuple[str, int]:
        length, pos = Codec.decode_varint(buff, pos)
        if pos + length > len(buff):
            raise ValueError('decode buffer not enough')
        return buff[pos:pos+length].decode('utf-8'), pos + length

    @staticmethod
    def decode_bytes(buff: bytes, pos: int) -> Tuple[bytes, int]:
        length, pos = Codec.decode_int32(buff, pos)
        if pos + length > len(buff):
            raise ValueError('decode buffer not enough')
        return buff[pos:pos+length], pos + length

    @staticmethod
    def decode_int32_list(buff: bytes, pos: int) -> Tuple[List[int], int]:
        count, pos = Codec.decode_int32(buff, pos)
        values = []
        for _ in range(count):
            val, pos = Codec.decode_int32(buff, pos)
            values.append(val)
        return values, pos

    @staticmethod
    def decode_int64_list(buff: bytes, pos: int) -> Tuple[List[int], int]:
        count, pos = Codec.decode_int32(buff, pos)
        values = []
        for _ in range(count):
            val, pos = Codec.decode_int64(buff, pos)
            values.append(val)
        return values, pos

    @staticmethod
    def decode_float_list(buff: bytes, pos: int) -> Tuple[List[float], int]:
        count, pos = Codec.decode_int32(buff, pos)
        values = []
        for _ in range(count):
            val, pos = Codec.decode_float32(buff, pos)
            values.append(val)
        return values, pos

    @staticmethod
    def decode_string_list(buff: bytes, pos: int) -> Tuple[List[str], int]:
        count, pos = Codec.decode_int32(buff, pos)
        values = []
        for _ in range(count):
            val, pos = Codec.decode_string(buff, pos)
            values.append(val)
        return values, pos
