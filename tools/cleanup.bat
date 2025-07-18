@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

REM 项目清理脚本 (Windows 批处理版本)
REM 用于清理 __pycache__, temp, 空文件, 空文件夹等内容

echo 🧹 开始清理项目...
echo ========================================

REM 获取项目根目录（脚本所在目录的父目录）
set "PROJECT_ROOT=%~dp0.."
pushd "%PROJECT_ROOT%"

REM 统计变量
set /a removed_items=0

echo 📁 清理 __pycache__ 目录...
for /f "delims=" %%d in ('dir /s /b /ad "__pycache__" 2^>nul') do (
    echo   删除: %%d
    rd /s /q "%%d" 2>nul
    set /a removed_items+=1
)

echo 📄 清理 Python 缓存文件...
for /f "delims=" %%f in ('dir /s /b "*.pyc" "*.pyo" 2^>nul') do (
    echo   删除: %%f
    del /q "%%f" 2>nul
    set /a removed_items+=1
)

echo 📁 清理 temp 目录内容...
for /f "delims=" %%d in ('dir /s /b /ad "temp" 2^>nul') do (
    echo   清理: %%d
    if exist "%%d" (
        pushd "%%d"
        for /f "delims=" %%f in ('dir /b 2^>nul') do (
            if exist "%%f" (
                if exist "%%f\*" (
                    rd /s /q "%%f" 2>nul
                ) else (
                    del /q "%%f" 2>nul
                )
            )
        )
        popd
        set /a removed_items+=1
    )
)

echo 📄 清理临时文件...
for %%ext in (tmp temp log) do (
    for /f "delims=" %%f in ('dir /s /b "*.%%ext" 2^>nul') do (
        echo   删除: %%f
        del /q "%%f" 2>nul
        set /a removed_items+=1
    )
)

REM 清理系统临时文件
for /f "delims=" %%f in ('dir /s /b "*~" ".DS_Store" "Thumbs.db" "desktop.ini" 2^>nul') do (
    echo   删除: %%f
    del /q "%%f" 2>nul
    set /a removed_items+=1
)

echo 📄 清理空文件...
for /f "delims=" %%f in ('dir /s /b 2^>nul ^| findstr /v "__init__.py"') do (
    if exist "%%f" (
        for %%a in ("%%f") do (
            if %%~za==0 (
                echo   删除空文件: %%f
                del /q "%%f" 2>nul
                set /a removed_items+=1
            )
        )
    )
)

popd

echo ========================================
echo ✅ 清理完成！
if !removed_items! gtr 0 (
    echo 总共清理了 !removed_items! 项内容
) else (
    echo 项目已经很干净了！
)

pause
