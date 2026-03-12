# cli-anything-midas-civil

MIDAS Civil NX 的完整命令行工具（CLI），将 MAPI（MIDAS API）封装为可用于自动化脚本和 AI Agent 的命令行接口。

## 环境要求

- Python 3.10+
- MIDAS Civil NX 已运行并启用 MAPI（`Apps > Connect`）
- MAPI Key（从 Civil NX 的 `Apps > API Settings` 获取）

## 安装

```bash
git clone https://github.com/isxylo/midas-civil-cli.git
cd midas-civil-cli
pip install -e .
```

验证安装：
```bash
cli-anything-midas-civil --help
```

## 全局选项

| 选项 | 说明 |
|------|------|
| `--key TEXT` | MAPI 认证密钥 |
| `--url TEXT` | MAPI Base URL |
| `--json` | 以 JSON 格式输出（适合脚本/Agent 使用） |

## 凭据配置

**方式一：环境变量**
```bash
export MIDAS_MAPI_KEY="your-mapi-key"
export MIDAS_BASE_URL="https://moa-engineers.midasit.com:443/civil"
```

**方式二：命令行参数**
```bash
cli-anything-midas-civil --key YOUR_KEY --url https://... status
```

**方式三：保存到本地会话**
```bash
cli-anything-midas-civil connect --key YOUR_KEY --url https://...
# 凭据保存至 ~/.midas_civil_session.json，后续命令无需重复输入
```

优先级：命令行参数 > 环境变量 > 会话文件

---

## 命令参考

### 连接管理

```bash
# 保存凭据并验证连接
cli-anything-midas-civil connect --key KEY --url URL

# 检查当前连接状态
cli-anything-midas-civil status
```

---

### model — 模型操作

```bash
cli-anything-midas-civil model new
cli-anything-midas-civil model open D:\\model.mcb
cli-anything-midas-civil model save
cli-anything-midas-civil model save --path D:\\model_new.mcb
cli-anything-midas-civil model analyse
cli-anything-midas-civil model units --force KN --length M --heat KJ --temp C
cli-anything-midas-civil model info --project "Bridge" --user "Engineer"
cli-anything-midas-civil model export D:\\model.json
cli-anything-midas-civil model export D:\\model.mct --format mct
cli-anything-midas-civil model import D:\\model.json
cli-anything-midas-civil model import D:\\model.mct --format mct
cli-anything-midas-civil model status
```

---

### node — 节点操作

```bash
cli-anything-midas-civil node add --x 0 --y 0 --z 0
cli-anything-midas-civil node add --x 1000 --y 0 --z 0 --id 2
cli-anything-midas-civil node list
cli-anything-midas-civil node get 1
cli-anything-midas-civil node sync
cli-anything-midas-civil node delete-all
```

---

### element — 单元操作

```bash
# 梁单元
cli-anything-midas-civil element beam --i-node 1 --j-node 2 --mat 1 --sect 1 --angle 0

# 桁架单元
cli-anything-midas-civil element truss --i-node 1 --j-node 2 --mat 1 --sect 1

# 板单元（3或4节点）
cli-anything-midas-civil element plate --nodes "1,2,3,4" --mat 1 --thick 1

cli-anything-midas-civil element list
cli-anything-midas-civil element get 1
cli-anything-midas-civil element sync
cli-anything-midas-civil element delete-all
```

---

### material — 材料操作

```bash
# 钢材料（--grade 为材料库中的牌号名称）
cli-anything-midas-civil material steel --name "Q345" --standard "GB(S)" --grade "Q345"

# 混凝土材料
cli-anything-midas-civil material concrete --name "C30" --standard "GB(RC)" --grade "C30"

# 用户自定义材料
cli-anything-midas-civil material user --name "Custom" --elasticity 200000 --poisson 0.3 --density 7.85e-9

cli-anything-midas-civil material list
cli-anything-midas-civil material get 1
```

---

### section — 截面操作

```bash
# 数据库截面
cli-anything-midas-civil section db --name "H400" --shape H --standard "GB" --dbname "HN400x200"

# 参数化截面（按尺寸）
cli-anything-midas-civil section value --name "Box" --shape B --dims "0.4,0.3,0.02,0.02"

# I 形截面
cli-anything-midas-civil section i-shape --name "I500" --dims "0.5,0.2,0.012,0.02,0.2,0.02"

# PSC 箱型截面
cli-anything-midas-civil section psc --name "PSC1" --dims "2.0,0.2,1.5,0.2,0.2,0.2"

# 变截面
cli-anything-midas-civil section tapered --name "Taper1" --sect-i 1 --sect-j 2

cli-anything-midas-civil section list
cli-anything-midas-civil section get 1
cli-anything-midas-civil section sync
cli-anything-midas-civil section delete-all
```

---

### thickness — 板厚操作

```bash
cli-anything-midas-civil thickness add --name "T20" --thick 20
cli-anything-midas-civil thickness add --name "T30" --thick 30 --thick-out 25
cli-anything-midas-civil thickness list
cli-anything-midas-civil thickness get 1
cli-anything-midas-civil thickness delete-all
```

---

### boundary — 边界条件

```bash
# 支撑（fix/pin/roller 或 6位字符串 TTTTFF）
cli-anything-midas-civil boundary support --nodes "1,2,3" --type fix
cli-anything-midas-civil boundary support --nodes 4 --type pin
cli-anything-midas-civil boundary list-supports
cli-anything-midas-civil boundary delete-supports

# 弹性连接
cli-anything-midas-civil boundary elastic-link --i-node 1 --j-node 2 --type GEN --sdx 1000
cli-anything-midas-civil boundary list-elastic-links
cli-anything-midas-civil boundary delete-elastic-links

# 刚性连接
cli-anything-midas-civil boundary rigid-link --master 1 --slaves "2,3,4" --dof 123456
cli-anything-midas-civil boundary list-rigid-links
cli-anything-midas-civil boundary delete-rigid-links

# 点弹簧
cli-anything-midas-civil boundary point-spring --node 1 --sdz 5000
cli-anything-midas-civil boundary list-springs
cli-anything-midas-civil boundary delete-springs

# 多线性力-变形函数
cli-anything-midas-civil boundary mlfc --name "NL1" --type FORCE --data "0,0,1,100,2,150"
cli-anything-midas-civil boundary list-mlfc
```

---

### group — 分组操作

```bash
# 结构组
cli-anything-midas-civil group structure-add --name "SG1" --nodes "1,2,3" --elems "1,2"
cli-anything-midas-civil group structure-list
cli-anything-midas-civil group structure-delete-all

# 边界组
cli-anything-midas-civil group boundary-add --name "BG1"
cli-anything-midas-civil group boundary-list

# 荷载组
cli-anything-midas-civil group load-add --name "LG1"
cli-anything-midas-civil group load-list
```

---

### load — 荷载操作

```bash
# 荷载工况
cli-anything-midas-civil load case --name "SW" --type D
cli-anything-midas-civil load list-cases
cli-anything-midas-civil load delete-case "SW"

# 自重
cli-anything-midas-civil load self-weight --case "SW" --dir Z --factor -1.0

# 节点荷载
cli-anything-midas-civil load nodal --nodes "3,4" --case "Wind" --fx 50.0 --fz -10.0
cli-anything-midas-civil load list-nodal

# 梁均布荷载
cli-anything-midas-civil load beam --elems "1,2" --case "Floor" --value -5.0 --dir GZ
cli-anything-midas-civil load list-beam

# 梁梯形荷载
cli-anything-midas-civil load beam-trapezoidal --elems "1" --case "Wind" \
  --d "0,0.5,1" --p "0,-10,-5" --dir GZ

# 板面压力荷载
cli-anything-midas-civil load pressure --elems "1" --case "Floor" --value -3.0 --dir GZ
cli-anything-midas-civil load list-pressure

# 荷载转质量
cli-anything-midas-civil load load-to-mass --dir XYZ --cases "SW,LL" --factors "1.0,0.5"
```

---

### loadcomb — 荷载组合

```bash
# 添加荷载组合（name:factor 格式）
cli-anything-midas-civil loadcomb add --name "ULS" --type Add --cases "SW:1.35,LL:1.5"
cli-anything-midas-civil loadcomb list
cli-anything-midas-civil loadcomb get 1
cli-anything-midas-civil loadcomb delete-all
```

---

### tendon — 预应力筋

```bash
# 预应力筋材料属性
cli-anything-midas-civil tendon property-add --name "T15" --rho 7.85e-9 \
  --ult-st 1860 --yield-st 1580
cli-anything-midas-civil tendon list-properties

# 预应力筋线形
cli-anything-midas-civil tendon profile-add --name "P1" --prop-id 1 --elems "1,2,3"
cli-anything-midas-civil tendon list-profiles

# 预应力张拉
cli-anything-midas-civil tendon prestress-add --profile "P1" --force 1000 --tension-type BOTH
cli-anything-midas-civil tendon list-prestress
```

---

### cs — 施工阶段

```bash
cli-anything-midas-civil cs add --name "CS1" --day 30
cli-anything-midas-civil cs list
cli-anything-midas-civil cs get 1
cli-anything-midas-civil cs delete-all
```

---

### movingload — 移动荷载

```bash
cli-anything-midas-civil movingload code-add HL93
cli-anything-midas-civil movingload list-codes

cli-anything-midas-civil movingload lane-add --name "Lane1" --elems "1,2,3" --ecc 0 --wheel-space 1.8
cli-anything-midas-civil movingload list-lanes
cli-anything-midas-civil movingload list-cases
```

---

### result — 结果提取（需先完成分析）

```bash
cli-anything-midas-civil result reaction --case "SW"
cli-anything-midas-civil result displacement --case "SW"
cli-anything-midas-civil result beam-force --case "SW"
cli-anything-midas-civil result beam-stress --case "SW"
cli-anything-midas-civil result beam-force-vbm --case "SW"
cli-anything-midas-civil result beam-stress-psc --case "SW"
cli-anything-midas-civil result truss-force --case "Wind"
cli-anything-midas-civil result truss-stress --case "Wind"
cli-anything-midas-civil result plate-force --case "Floor"
cli-anything-midas-civil result table --type BEAMFORCE --case "SW"
```

---

### api — 原始 MAPI 透传

```bash
cli-anything-midas-civil api get /db/NODE
cli-anything-midas-civil api get /db/UNIT
cli-anything-midas-civil api put /db/UNIT --body '{"Assign":{"1":{"FORCE":"KN","DIST":"M","HEAT":"KJ","TEMPER":"C"}}}'
cli-anything-midas-civil api post /doc/NEW --body '{}'
cli-anything-midas-civil api delete /db/NODE/1
```

---

### repl — 交互式模式

```bash
cli-anything-midas-civil repl
# midas-civil> node add --x 0 --y 0 --z 0
# midas-civil> node list
# midas-civil> exit
```

---

## 常用 Base URL

| 地区 | URL |
|------|-----|
| 全球（默认） | `https://moa-engineers.midasit.com:443/civil` |
| 中国 | `https://moa-engineers.midasit.cn:443/civil` |
| 韩国 | `https://moa-engineers-kr.midasit.com:443/civil` |
| 欧洲 | `https://moa-engineers-gb.midasit.com:443/civil` |
| 美国 | `https://moa-engineers-us.midasit.com:443/civil` |
| 印度 | `https://moa-engineers-in.midasit.com:443/civil` |

---

## 架构说明

```
cli-anything-midas-civil (Click CLI)
  └── cli_anything.midas_civil.core
        ├── Connection        — 认证 HTTP 请求封装
        ├── Session           — 凭据本地持久化
        ├── ModelOps          — 模型级操作
        ├── NodeOps           — 节点 CRUD
        ├── ElementOps        — 单元 CRUD（梁/桁架/板）
        ├── MaterialOps       — 材料定义
        ├── SectionOps        — 截面定义
        ├── ThicknessOps      — 板厚定义
        ├── BoundaryOps       — 支座/弹性连接/刚性连接/点弹簧
        ├── GroupOps          — 结构组/边界组/荷载组
        ├── LoadOps           — 荷载工况与荷载
        ├── LoadCombOps       — 荷载组合
        ├── TendonOps         — 预应力筋
        ├── ConstructionOps   — 施工阶段
        ├── MovingLoadOps     — 移动荷载
        └── ResultOps         — 分析结果提取
```
