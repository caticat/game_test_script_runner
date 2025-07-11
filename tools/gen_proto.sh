#!/bin/bash

# 设置 proto 文件所在路径（源路径，使用 Windows 路径转为 WSL/MINGW 路径）
SRC_PROTO_DIR="Q:/kof/dev/server/kof_server/server/public/proto"

# 设置生成目标路径
DST_OUTPUT_DIR="Q:/kof/dev/proto_python"

# 创建目标目录（若不存在）
mkdir -p "$DST_OUTPUT_DIR"

# 切换到 proto 源目录
cd "$SRC_PROTO_DIR" || { echo "进入源目录失败: $SRC_PROTO_DIR"; exit 1; }

# 查找所有 .proto 文件并生成 Python 代码
for file in *.proto; do
    echo "正在处理: $file"
    protoc -I. --python_out="$DST_OUTPUT_DIR" "$file"
done

echo "✅ 所有 proto 文件已生成到: $DST_OUTPUT_DIR"
cd -
