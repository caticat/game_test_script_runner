# 协议编解码器

import struct
from typing import Tuple


class Codec:
    """协议编解码器"""
    
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
    def encode_float32(value: float) -> bytes:
        return struct.pack('<f', value)

    @staticmethod
    def encode_float64(value: float) -> bytes:
        return struct.pack('<d', value)

    @staticmethod
    def encode_string(value: str) -> bytes:
        utf8_bytes = value.encode('utf-8')
        length = len(utf8_bytes)
        return Codec.encode_varint(length) + utf8_bytes

    @staticmethod
    def encode_bytes(value: bytes) -> bytes:
        length = len(value)
        return Codec.encode_varint(length) + value

    @staticmethod
    def decode_bool(data: bytes, pos: int) -> Tuple[bool, int]:
        if pos >= len(data):
            raise ValueError("数据不足")
        return data[pos] != 0, pos + 1

    @staticmethod
    def decode_int8(data: bytes, pos: int) -> Tuple[int, int]:
        if pos >= len(data):
            raise ValueError("数据不足")
        value = struct.unpack('<b', data[pos:pos+1])[0]
        return value, pos + 1

    @staticmethod
    def decode_uint8(data: bytes, pos: int) -> Tuple[int, int]:
        if pos >= len(data):
            raise ValueError("数据不足")
        value = struct.unpack('<B', data[pos:pos+1])[0]
        return value, pos + 1

    @staticmethod
    def decode_varint(data: bytes, pos: int) -> Tuple[int, int]:
        value = 0
        shift = 0
        while pos < len(data):
            byte = data[pos]
            pos += 1
            value |= (byte & 0x7F) << shift
            if (byte & 0x80) == 0:
                break
            shift += 7
        return value, pos

    @staticmethod
    def decode_int16(data: bytes, pos: int) -> Tuple[int, int]:
        value, pos = Codec.decode_varint(data, pos)
        if value & 0x8000:
            value |= 0xFFFF0000
        return value, pos

    @staticmethod
    def decode_uint16(data: bytes, pos: int) -> Tuple[int, int]:
        return Codec.decode_varint(data, pos)

    @staticmethod
    def decode_int32(data: bytes, pos: int) -> Tuple[int, int]:
        value, pos = Codec.decode_varint(data, pos)
        if value & 0x80000000:
            value |= 0xFFFFFFFF00000000
        return value, pos

    @staticmethod
    def decode_uint32(data: bytes, pos: int) -> Tuple[int, int]:
        return Codec.decode_varint(data, pos)

    @staticmethod
    def decode_int64(data: bytes, pos: int) -> Tuple[int, int]:
        return Codec.decode_varint(data, pos)

    @staticmethod
    def decode_uint64(data: bytes, pos: int) -> Tuple[int, int]:
        return Codec.decode_varint(data, pos)

    @staticmethod
    def decode_float32(data: bytes, pos: int) -> Tuple[float, int]:
        if pos + 4 > len(data):
            raise ValueError("数据不足")
        value = struct.unpack('<f', data[pos:pos+4])[0]
        return value, pos + 4

    @staticmethod
    def decode_float64(data: bytes, pos: int) -> Tuple[float, int]:
        if pos + 8 > len(data):
            raise ValueError("数据不足")
        value = struct.unpack('<d', data[pos:pos+8])[0]
        return value, pos + 8

    @staticmethod
    def decode_string(data: bytes, pos: int) -> Tuple[str, int]:
        length, pos = Codec.decode_varint(data, pos)
        if pos + length > len(data):
            raise ValueError("数据不足")
        value = data[pos:pos+length].decode('utf-8')
        return value, pos + length

    @staticmethod
    def decode_bytes(data: bytes, pos: int) -> Tuple[bytes, int]:
        length, pos = Codec.decode_varint(data, pos)
        if pos + length > len(data):
            raise ValueError("数据不足")
        value = data[pos:pos+length]
        return value, pos + length
