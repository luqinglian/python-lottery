# Python 抽奖小程序 🎲

一个**零依赖**的命令行抽奖工具，用 Python 3 标准库写成，开箱即用。

## 特性

- ✅ 从名单中随机抽取任意数量的中奖者
- ✅ 默认**不重复中奖**，也可用 `--allow-repeat` 允许重复
- ✅ 支持**权重抽奖**：`张三:3` 表示张三中奖概率是普通人的 3 倍
- ✅ 支持 `--seed` 固定随机种子，结果可复现（适合公开抽奖留证）
- ✅ 支持文本与 JSON 两种输出
- ✅ 附带完整单元测试

## 快速开始

```bash
# 内联名单
python3 lottery.py -p "张三,李四,王五,赵六" -n 2

# 带权重
python3 lottery.py -p "张三:3,李四:1,王五:1" -n 1

# 结果可复现
python3 lottery.py -p "A,B,C,D" -n 2 --seed 2024

# 从文件读名单（每行一个，支持 名字:权重）
python3 lottery.py -f names.txt -n 3

# JSON 输出，方便接入其它程序
python3 lottery.py -p "A,B,C" -n 1 --json
```

输出示例：

```
共 4 人参与，抽取 2 位：
  1. 王五
  2. 张三
```

## 参数说明

| 参数 | 说明 |
| --- | --- |
| `-p, --participants` | 名单，逗号或换行分隔，可写 `名字:权重` |
| `-f, --file` | 从文件读取名单 |
| `-n, --count` | 中奖人数，默认 1 |
| `--seed` | 随机种子，指定后结果可复现 |
| `--allow-repeat` | 允许同一个人重复中奖 |
| `--json` | 以 JSON 格式输出 |

不传 `-p` 或 `-f` 时，会从标准输入读取名单，例如：

```bash
cat names.txt | python3 lottery.py -n 2
```

## 运行测试

```bash
python3 -m unittest -v
```

测试覆盖了名单解析、权重校验、中奖去重、种子可复现性以及权重偏向性。

## 项目结构

```
lottery.py        # 核心逻辑 + 命令行入口
test_lottery.py   # 单元测试
```

## 许可

MIT
