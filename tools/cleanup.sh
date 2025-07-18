#!/bin/bash

# 项目清理脚本
# 用于清理 __pycache__, temp, 空文件, 空文件夹等内容
# 可在git-bash下运行

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取脚本所在目录的父目录（项目根目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}🧹 开始清理项目: $PROJECT_ROOT${NC}"
echo "========================================"

# 统计变量
removed_pycache=0
removed_temp=0
removed_empty_files=0
removed_empty_dirs=0

# 1. 清理 __pycache__ 目录
echo -e "${YELLOW}📁 清理 __pycache__ 目录...${NC}"
while IFS= read -r -d '' dir; do
    echo "  删除: $dir"
    rm -rf "$dir"
    ((removed_pycache++))
done < <(find "$PROJECT_ROOT" -type d -name "__pycache__" -print0 2>/dev/null || true)

if [ $removed_pycache -eq 0 ]; then
    echo "  ✅ 没有找到 __pycache__ 目录"
else
    echo -e "  ${GREEN}✅ 已删除 $removed_pycache 个 __pycache__ 目录${NC}"
fi

# 2. 清理 temp 目录内容（保留目录本身）
echo -e "${YELLOW}📁 清理 temp 目录内容...${NC}"
while IFS= read -r -d '' dir; do
    if [ -d "$dir" ]; then
        echo "  清理目录: $dir"
        # 删除目录内的所有内容但保留目录本身
        find "$dir" -mindepth 1 -delete 2>/dev/null || true
        ((removed_temp++))
    fi
done < <(find "$PROJECT_ROOT" -type d -name "temp" -print0 2>/dev/null || true)

if [ $removed_temp -eq 0 ]; then
    echo "  ✅ 没有找到 temp 目录"
else
    echo -e "  ${GREEN}✅ 已清理 $removed_temp 个 temp 目录${NC}"
fi

# 3. 清理 .pyc 文件
echo -e "${YELLOW}📄 清理 .pyc 文件...${NC}"
removed_pyc=0
while IFS= read -r -d '' file; do
    echo "  删除: $file"
    rm -f "$file"
    ((removed_pyc++))
done < <(find "$PROJECT_ROOT" -type f -name "*.pyc" -print0 2>/dev/null || true)

if [ $removed_pyc -eq 0 ]; then
    echo "  ✅ 没有找到 .pyc 文件"
else
    echo -e "  ${GREEN}✅ 已删除 $removed_pyc 个 .pyc 文件${NC}"
fi

# 4. 清理 .pyo 文件
echo -e "${YELLOW}📄 清理 .pyo 文件...${NC}"
removed_pyo=0
while IFS= read -r -d '' file; do
    echo "  删除: $file"
    rm -f "$file"
    ((removed_pyo++))
done < <(find "$PROJECT_ROOT" -type f -name "*.pyo" -print0 2>/dev/null || true)

if [ $removed_pyo -eq 0 ]; then
    echo "  ✅ 没有找到 .pyo 文件"
else
    echo -e "  ${GREEN}✅ 已删除 $removed_pyo 个 .pyo 文件${NC}"
fi

# 5. 清理空文件
echo -e "${YELLOW}📄 清理空文件...${NC}"
while IFS= read -r -d '' file; do
    # 跳过一些特殊的空文件（如 __init__.py）
    basename_file=$(basename "$file")
    if [[ "$basename_file" == "__init__.py" ]]; then
        continue
    fi
    
    echo "  删除空文件: $file"
    rm -f "$file"
    ((removed_empty_files++))
done < <(find "$PROJECT_ROOT" -type f -empty -print0 2>/dev/null || true)

if [ $removed_empty_files -eq 0 ]; then
    echo "  ✅ 没有找到空文件"
else
    echo -e "  ${GREEN}✅ 已删除 $removed_empty_files 个空文件${NC}"
fi

# 6. 清理空目录（多次执行以处理嵌套的空目录）
echo -e "${YELLOW}📁 清理空目录...${NC}"
for i in {1..5}; do
    removed_in_pass=0
    while IFS= read -r -d '' dir; do
        # 跳过项目根目录和一些重要目录
        if [[ "$dir" == "$PROJECT_ROOT" ]] || \
           [[ "$dir" == "$PROJECT_ROOT/.git" ]] || \
           [[ "$dir" =~ \.git/ ]]; then
            continue
        fi
        
        echo "  删除空目录: $dir"
        rmdir "$dir" 2>/dev/null || true
        ((removed_in_pass++))
        ((removed_empty_dirs++))
    done < <(find "$PROJECT_ROOT" -type d -empty -print0 2>/dev/null || true)
    
    if [ $removed_in_pass -eq 0 ]; then
        break
    fi
done

if [ $removed_empty_dirs -eq 0 ]; then
    echo "  ✅ 没有找到空目录"
else
    echo -e "  ${GREEN}✅ 已删除 $removed_empty_dirs 个空目录${NC}"
fi

# 7. 清理常见的临时文件
echo -e "${YELLOW}📄 清理常见临时文件...${NC}"
temp_patterns=(
    "*.tmp"
    "*.temp"
    "*~"
    ".DS_Store"
    "Thumbs.db"
    "desktop.ini"
)

removed_temp_files=0
for pattern in "${temp_patterns[@]}"; do
    while IFS= read -r -d '' file; do
        echo "  删除临时文件: $file"
        rm -f "$file"
        ((removed_temp_files++))
    done < <(find "$PROJECT_ROOT" -type f -name "$pattern" -print0 2>/dev/null || true)
done

if [ $removed_temp_files -eq 0 ]; then
    echo "  ✅ 没有找到临时文件"
else
    echo -e "  ${GREEN}✅ 已删除 $removed_temp_files 个临时文件${NC}"
fi

# 8. 清理日志文件（可选）
echo -e "${YELLOW}📄 清理 .log 文件...${NC}"
removed_logs=0
while IFS= read -r -d '' file; do
    echo "  删除日志文件: $file"
    rm -f "$file"
    ((removed_logs++))
done < <(find "$PROJECT_ROOT" -type f -name "*.log" -print0 2>/dev/null || true)

if [ $removed_logs -eq 0 ]; then
    echo "  ✅ 没有找到 .log 文件"
else
    echo -e "  ${GREEN}✅ 已删除 $removed_logs 个 .log 文件${NC}"
fi

# 9. 显示项目大小（可选）
echo -e "${YELLOW}📊 计算项目大小...${NC}"
if command -v du >/dev/null 2>&1; then
    project_size=$(du -sh "$PROJECT_ROOT" 2>/dev/null | cut -f1 || echo "未知")
    echo -e "  项目总大小: ${BLUE}$project_size${NC}"
fi

# 总结报告
echo ""
echo "========================================"
echo -e "${GREEN}🎉 清理完成！${NC}"
echo ""
echo "清理统计:"
echo "  - __pycache__ 目录: $removed_pycache 个"
echo "  - temp 目录: $removed_temp 个"
echo "  - .pyc 文件: $removed_pyc 个"
echo "  - .pyo 文件: $removed_pyo 个"
echo "  - 空文件: $removed_empty_files 个"
echo "  - 空目录: $removed_empty_dirs 个"
echo "  - 临时文件: $removed_temp_files 个"
echo "  - 日志文件: $removed_logs 个"
echo ""

total_removed=$((removed_pycache + removed_temp + removed_pyc + removed_pyo + removed_empty_files + removed_empty_dirs + removed_temp_files + removed_logs))
if [ $total_removed -gt 0 ]; then
    echo -e "${GREEN}总共清理了 $total_removed 项内容${NC}"
else
    echo -e "${GREEN}项目已经很干净了！${NC}"
fi

echo -e "${BLUE}✨ 清理脚本执行完毕${NC}"
