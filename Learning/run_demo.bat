@echo off
REM ============================================================================
REM RAG 学习中心 - 快速启动脚本 (Windows)
REM ============================================================================
REM 用途: 快速运行所有 Demo 和生成示例文档
REM ============================================================================

echo.
echo 🟦 RAG 学习中心 - 快速启动脚本 🟦
echo.
echo 本脚本将为你自动运行所有演示和检查文件。
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到 Python
    echo 请先安装 Python 3.7+ (https://www.python.org)
    pause
    exit /b 1
)

echo ✓ 检测到 Python
python --version
echo.

REM 获取脚本位置
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo 当前目录: %SCRIPT_DIR%
echo.

REM ============================================================================
REM 第一部分: 运行 Day 1 演示
REM ============================================================================
echo.
echo 🟦 开始 Day 1 - RAG 核心概念演示...
echo ============================================================================
echo.

if exist "25_12_22.py" (
    echo ✓ 运行 25_12_22.py ...
    echo.
    python 25_12_22.py
    echo.
    echo ✓ Day 1 演示完成！
) else (
    echo ❌ 错误: 找不到 25_12_22.py
)

echo.
pause /m "按任意键继续到 Day 3 Demo..."
echo.

REM ============================================================================
REM 第二部分: 运行 Day 3 演示
REM ============================================================================
echo.
echo 🟦 开始 Day 3 - RAG 完整 Demo 演示...
echo ============================================================================
echo.

if exist "RAG_Day3_Demo.py" (
    echo ✓ 运行 RAG_Day3_Demo.py ...
    echo.
    python RAG_Day3_Demo.py
    echo.
    echo ✓ Day 3 演示完成！
) else (
    echo ❌ 错误: 找不到 RAG_Day3_Demo.py
)

echo.
echo ============================================================================
echo ✅ 所有演示已完成！
echo ============================================================================
echo.
echo 📚 接下来的步骤:
echo.
echo 1. 快速了解:
echo    - 打开并阅读 QuickReference.md (10 分钟)
echo    - 打开并阅读 INDEX.md (导航)
echo.
echo 2. 标准学习:
echo    - 按 README.md 的学习路线完整学习 (8-10 小时)
echo.
echo 3. 业务诊断:
echo    - 学习 RAG_Day2_Business_Adaptation.md 中的 5 问诊断法
echo    - 用这个方法诊断你遇到的被投公司
echo.
echo 4. 实战应用:
echo    - 修改 RAG_Day3_Demo.py 用自己的文档
echo    - 给创始人做一个 5 分钟的 Demo
echo.
echo 📁 关键文件位置:
echo    - 索引: INDEX.md
echo    - 学习路线: README.md
echo    - 快速参考: QuickReference.md
echo    - 学习检查: LearningChecklist.md
echo    - 演示示例: sample_docs/
echo.
echo 💡 记住:
echo    "不是模型更聪明，是它终于能看你们的数据了。"
echo.
pause
