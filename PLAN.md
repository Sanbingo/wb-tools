# WB 财务分析系统 - 开发计划

## 技术栈
- **后端**: FastAPI + SQLite (port 7778)
- **前端**: React 18 + Ant Design
- **部署**: Nginx (`/usr/share/nginx/html/wbtools/`)
- **数据源**: Wildberries Statistics API

## 核心功能
1. **仪表盘** - 当日/当月销售额、订单数、退货、佣金、净利润
2. **销售分析** - 按日/月趋势图、商品排行
3. **订单管理** - 订单列表、状态追踪
4. **库存概览** - 库存量、价值
5. **财务报告** - P&L 汇总、费用明细
6. **数据同步** - 定时刷新 + 手动刷新

## 页面结构
```
Dashboard       → 关键指标卡片 + 趋势图
Sales Analysis  → 销售额趋势、商品排行、每日明细
Orders          → 订单列表、搜索、筛选
Stocks          → 库存列表、仓库分布
Reports         → 财务汇总、费用分析
```

## 目录结构
```
/home/admin/wbtools/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   ├── api/
│   │   └── services/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   └── services/
│   └── package.json
└── PLAN.md
```
