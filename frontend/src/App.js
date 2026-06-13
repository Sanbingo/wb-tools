import React, { useState, useEffect } from 'react';
import { Layout, Menu, Card, Row, Col, Statistic, Table, Tag, Button, Space, Typography, Spin, message, Empty, DatePicker, Alert } from 'antd';
import { SyncOutlined, DashboardOutlined, ShoppingCartOutlined, InboxOutlined, BarChartOutlined, CloudSyncOutlined, DownloadOutlined } from '@ant-design/icons';
import { Line, Column, Pie } from '@ant-design/plots';

const { RangePicker } = DatePicker;

const { Header, Sider, Content } = Layout;
const { Title } = Typography;

// ======================== API ========================
const API = '/api/v1';

async function fetchAPI(path) {
  const resp = await fetch(`${API}${path}`);
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  return resp.json();
}

async function postAPI(path, body) {
  const resp = await fetch(`${API}${path}`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  return resp.json();
}

function formatMoney(n) {
  return (n || 0).toLocaleString('ru-RU', {minimumFractionDigits: 2, maximumFractionDigits: 2});
}

function formatDate(d) {
  if (!d) return '-';
  return d.split('T')[0];
}

// ======================== DASHBOARD ========================
function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAPI('/dashboard').then(d => { setData(d); setLoading(false); }).catch(() => { message.error('加载失败'); setLoading(false); });
  }, []);

  if (loading) return <Spin size="large" style={{display:'block',margin:'100px auto'}}/>;
  if (!data) return <Empty description="暂无数据，请先同步" />;

  const today = data.today || {};
  const month = data.this_month || {};
  const stocks = data.stocks || {};
  const trend = data.trend || [];

  const trendData = trend.map(t => ({date: t.date, sales: t.sales, forPay: t.for_pay}));

  return (
    <div>
      <Title level={4}>📊 财务概览</Title>
      <Row gutter={[16,16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card><Statistic title="今日销售额" value={today.sales || 0} prefix="₽" precision={2} valueStyle={{color:'#cf1322'}}/></Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card><Statistic title="今日实收" value={today.for_pay || 0} prefix="₽" precision={2} valueStyle={{color:'#3f8600'}}/></Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card><Statistic title="今日订单" value={today.orders || 0} suffix="单"/></Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card><Statistic title="今日佣金" value={today.commission || 0} prefix="₽" precision={2} valueStyle={{color:'#faad14'}}/></Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card><Statistic title="本月销售额" value={month.sales || 0} prefix="₽" precision={2}/></Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card><Statistic title="本月实收" value={month.for_pay || 0} prefix="₽" precision={2} valueStyle={{color:'#3f8600'}}/></Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card><Statistic title="本月订单" value={month.orders || 0} suffix="单"/></Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card><Statistic title="库存总值" value={stocks.total_value || 0} prefix="₽" precision={2}/></Card>
        </Col>
      </Row>

      <Card title="📈 近7天销售趋势" style={{marginTop:16}}>
        {trendData.length > 0 ? (
          <Line data={trendData} xField="date" yField="sales" smooth point={{size:3}} height={300} />
        ) : <Empty description="暂无趋势数据" />}
      </Card>

      <Card title="⚡ 快速操作" style={{marginTop:16}}>
        <Space>
          <Button type="primary" icon={<SyncOutlined />} onClick={async () => {
            message.loading({content:'同步中...', key:'sync'});
            try {
              const r = await postAPI('/sync/all');
              message.success({content:`同步完成！销售:${r.sales?.new_records||0} 订单:${r.orders?.new_records||0} 库存:${r.stocks?.records||0}`, key:'sync'});
              setTimeout(() => window.location.reload(), 1000);
            } catch(e) { message.error({content:'同步失败', key:'sync'}); }
          }}>同步所有数据</Button>
        </Space>
      </Card>
    </div>
  );
}

// ======================== SALES ANALYSIS ========================
function SalesAnalysis() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [topProducts, setTopProducts] = useState(null);

  useEffect(() => {
    Promise.all([
      fetchAPI(`/sales?page=${page}&page_size=20`),
      fetchAPI('/products/top?days=30&limit=10'),
    ]).then(([sales, top]) => {
      setData(sales);
      setTopProducts(top);
      setLoading(false);
    }).catch(() => { message.error('加载失败'); setLoading(false); });
  }, [page]);

  if (loading) return <Spin size="large" style={{display:'block',margin:'100px auto'}}/>;

  const columns = [
    {title:'日期', dataIndex:'date', render:d=>formatDate(d), width:80},
    {title:'商品', dataIndex:'supplier_article', ellipsis:true},
    {title:'NM ID', dataIndex:'nm_id', width:100},
    {title:'品类', dataIndex:'subject', width:80},
    {title:'总价', dataIndex:'total_price', render:v=>`₽${formatMoney(v)}`, width:100, sorter:(a,b)=>a.total_price-b.total_price},
    {title:'折扣', dataIndex:'discount_percent', render:v=>`${v}%`, width:60},
    {title:'实收', dataIndex:'for_pay', render:v=>`₽${formatMoney(v)}`, width:100, sorter:(a,b)=>a.for_pay-b.for_pay},
    {title:'仓库', dataIndex:'warehouse_name', width:100},
  ];

  const topData = (topProducts?.items || []).map(p => ({
    article: (p.article || '').substring(0, 12) || String(p.nm_id),
    revenue: p.revenue
  }));

  return (
    <div>
      <Title level={4}>📦 销售明细</Title>
      <Row gutter={16}>
        <Col xs={24} lg={16}>
          <Card>
            <Table
              dataSource={data?.items || []}
              columns={columns}
              rowKey="id"
              size="small"
              pagination={{
                current: page,
                total: data?.total || 0,
                pageSize: 20,
                onChange: p => setPage(p),
                showTotal: t => `共 ${t} 条`,
              }}
            />
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="🏆 热销商品 TOP 10">
            {topData.length > 0 ? (
              <Column data={topData} xField="article" yField="revenue" height={400} />
            ) : <Empty description="暂无数据" />}
          </Card>
        </Col>
      </Row>
    </div>
  );
}

// ======================== ORDERS ========================
function Orders() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    let path = `/orders?page=${page}&page_size=20`;
    if (filter === 'cancelled') path += '&is_cancel=true';
    else if (filter === 'active') path += '&is_cancel=false';
    fetchAPI(path).then(d => { setData(d); setLoading(false); }).catch(() => { message.error('加载失败'); setLoading(false); });
  }, [page, filter]);

  if (loading) return <Spin size="large" style={{display:'block',margin:'100px auto'}}/>;

  const columns = [
    {title:'日期', dataIndex:'date', render:d=>formatDate(d), width:80},
    {title:'商品', dataIndex:'supplier_article', ellipsis:true},
    {title:'总价', dataIndex:'total_price', render:v=>`₽${formatMoney(v)}`, width:100},
    {title:'折扣', dataIndex:'discount_percent', render:v=>`${v}%`, width:60},
    {title:'成交价', dataIndex:'finished_price', render:v=>`₽${formatMoney(v)}`, width:100},
    {title:'状态', dataIndex:'is_cancel', render:v=>v ? <Tag color="red">已取消</Tag> : <Tag color="green">有效</Tag>, width:60},
    {title:'仓库', dataIndex:'warehouse_name', width:100},
    {title:'地区', dataIndex:'region_name', width:100, ellipsis:true},
  ];

  return (
    <div>
      <Title level={4}>📋 订单列表</Title>
      <Card>
        <Space style={{marginBottom:16}}>
          <Button type={filter==='all'?'primary':'default'} onClick={()=>{setFilter('all');setPage(1)}}>全部</Button>
          <Button type={filter==='active'?'primary':'default'} onClick={()=>{setFilter('active');setPage(1)}}>有效</Button>
          <Button type={filter==='cancelled'?'primary':'default'} onClick={()=>{setFilter('cancelled');setPage(1)}}>已取消</Button>
        </Space>
        <Table
          dataSource={data?.items || []}
          columns={columns}
          rowKey="id"
          size="small"
          pagination={{
            current: page,
            total: data?.total || 0,
            pageSize: 20,
            onChange: p => setPage(p),
            showTotal: t => `共 ${t} 条`,
          }}
        />
      </Card>
    </div>
  );
}

// ======================== STOCKS ========================
function Stocks() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAPI('/stocks?page=1&page_size=20').then(d => { setData(d); setLoading(false); }).catch(() => { message.error('加载失败'); setLoading(false); });
  }, []);

  if (loading) return <Spin size="large" style={{display:'block',margin:'100px auto'}}/>;

  const warehouseData = data?.warehouses?.map(w => ({name: w.name, value: w.value})) || [];
  const totalValue = (data?.items || []).reduce((s, i) => s + (i.total_value || 0), 0);

  const columns = [
    {title:'商品', dataIndex:'supplier_article', ellipsis:true, width:150},
    {title:'NM ID', dataIndex:'nm_id', width:100},
    {title:'仓库', dataIndex:'warehouse_name', width:100},
    {title:'库存', dataIndex:'quantity', width:60},
    {title:'在途去客户', dataIndex:'in_way_to_client', width:80},
    {title:'在途回仓库', dataIndex:'in_way_from_client', width:80},
    {title:'单价', dataIndex:'price', render:v=>`₽${formatMoney(v)}`, width:80},
    {title:'总价值', dataIndex:'total_value', render:v=>`₽${formatMoney(v)}`, width:100, sorter:(a,b)=>a.total_value-b.total_value},
    {title:'品类', dataIndex:'subject', width:80},
  ];

  return (
    <div>
      <Title level={4}>📦 库存概览</Title>
      <Row gutter={16}>
        <Col span={6}><Card><Statistic title="SKU 总数" value={data?.total || 0} /></Card></Col>
        <Col span={6}><Card><Statistic title="库存总值" value={totalValue} prefix="₽" precision={2}/></Card></Col>
      </Row>
      <Row gutter={16} style={{marginTop:16}}>
        <Col xs={24} lg={8}>
          <Card title="仓库分布">
            {warehouseData.length > 0 ? (
              <Pie data={warehouseData} angleField="value" colorField="name" height={300} />
            ) : <Empty description="暂无数据" />}
          </Card>
        </Col>
        <Col xs={24} lg={16}>
          <Card>
            <Table dataSource={data?.items || []} columns={columns} rowKey="id" size="small" pagination={{pageSize:20, showTotal:t=>`共 ${t} 条`}} />
          </Card>
        </Col>
      </Row>
    </div>
  );
}

// ======================== REPORTS ========================
function Reports() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [fetching, setFetching] = useState(false);
  const [dates, setDates] = useState(null);
  const [downloadUrl, setDownloadUrl] = useState(null);
  const [exchangeRate, setExchangeRate] = useState(12.5);
  const [taxRate, setTaxRate] = useState(12);
  const [feeRate, setFeeRate] = useState(7);

  useEffect(() => {
    Promise.all([
      fetchAPI('/reports/daily?days=30'),
      fetchAPI('/reports/summary?days=30'),
    ]).then(([daily, summary]) => {
      setData({daily, summary});
      setLoading(false);
    }).catch(() => { message.error('加载失败'); setLoading(false); });
  }, []);

  const handleAutoFetch = async () => {
    if (!dates || !dates[0] || !dates[1]) {
      message.warning('请先选择日期范围');
      return;
    }
    setFetching(true);
    setDownloadUrl(null);
    const startDate = dates[0].format('YYYY-MM-DD');
    const endDate = dates[1].format('YYYY-MM-DD');
    
    message.loading({ content: `正在从 WB 拉取 ${startDate} ~ ${endDate} 报表...`, key: 'fetch' });
    try {
      const formData = new FormData();
      formData.append('start_date', startDate);
      formData.append('end_date', endDate);
      formData.append('exchange_rate', String(exchangeRate));
      formData.append('tax_rate', String(taxRate));
      formData.append('fee_rate', String(feeRate));
      
      const resp = await fetch(`${API}/reports/fetch-auto`, {
        method: 'POST',
        body: formData,
      });
      if (!resp.ok) {
        const err = await resp.json();
        throw new Error(err.detail || `HTTP ${resp.status}`);
      }
      const result = await resp.json();
      setDownloadUrl(result.download_url);
      const s = result.stats;
      message.success({ 
        content: `✅ 分析完成！共 ${s.total_rows} 条记录，${s.products} 个商品`,
        key: 'fetch',
        duration: 5,
      });
    } catch (e) {
      message.error({ content: `❌ 失败: ${e.message}`, key: 'fetch', duration: 5 });
    } finally {
      setFetching(false);
    }
  };

  if (loading) return <Spin size="large" style={{display:'block',margin:'100px auto'}}/>;
  if (!data) return <Empty description="暂无数据" />;

  const s = data.summary || {};
  const dailyData = (data.daily?.items || []).slice().reverse();

  const columns = [
    {title:'日期', dataIndex:'date', render:d=>formatDate(d)},
    {title:'销售额', dataIndex:'sales', render:v=>`₽${formatMoney(v)}`},
    {title:'实收', dataIndex:'for_pay', render:v=>`₽${formatMoney(v)}`},
    {title:'订单数', dataIndex:'orders'},
    {title:'佣金', dataIndex:'commission', render:v=>`₽${formatMoney(v)}`},
    {title:'退货', dataIndex:'cancelled'},
    {title:'平均折扣', dataIndex:'avg_discount', render:v=>`${v}%`},
  ];

  return (
    <div>
      <Title level={4}>📊 财务报表</Title>

      {/* Auto-fetch section */}
      <Card title="🚀 自动拉取 WB 报表" style={{marginBottom: 16}}>
        <Space direction="vertical" style={{width: '100%'}} size="middle">
          <Row gutter={[16,16]} align="middle">
            <Col xs={24} md={8}>
              <RangePicker 
                style={{width: '100%'}}
                onChange={(d) => setDates(d)}
                placeholder={['开始日期', '结束日期']}
              />
            </Col>
            <Col xs={12} md={4}>
              <div>
                <div style={{fontSize:12,color:'#888',marginBottom:4}}>汇率 (₽→¥)</div>
                <input 
                  type="number" step="0.1" value={exchangeRate}
                  onChange={e => setExchangeRate(Number(e.target.value))}
                  style={{width:'100%',padding:'4px 8px',border:'1px solid #d9d9d9',borderRadius:4}}
                />
              </div>
            </Col>
            <Col xs={12} md={4}>
              <div>
                <div style={{fontSize:12,color:'#888',marginBottom:4}}>税率 %</div>
                <input 
                  type="number" step="0.1" value={taxRate}
                  onChange={e => setTaxRate(Number(e.target.value))}
                  style={{width:'100%',padding:'4px 8px',border:'1px solid #d9d9d9',borderRadius:4}}
                />
              </div>
            </Col>
            <Col xs={12} md={4}>
              <div>
                <div style={{fontSize:12,color:'#888',marginBottom:4}}>手续费率 %</div>
                <input 
                  type="number" step="0.1" value={feeRate}
                  onChange={e => setFeeRate(Number(e.target.value))}
                  style={{width:'100%',padding:'4px 8px',border:'1px solid #d9d9d9',borderRadius:4}}
                />
              </div>
            </Col>
            <Col xs={12} md={4}>
              <Button 
                type="primary" 
                icon={<DownloadOutlined />}
                onClick={handleAutoFetch}
                loading={fetching}
                size="large"
                style={{width:'100%', marginTop: 20}}
              >
                {fetching ? '拉取中...' : '自动分析'}
              </Button>
            </Col>
          </Row>

          {downloadUrl && (
            <Alert
              type="success"
              showIcon
              message="分析完成！"
              description={
                <div>
                  <span>利润表已生成，</span>
                  <a href={downloadUrl} download style={{fontWeight:'bold',fontSize:16}}>点击下载 Excel 文件</a>
                </div>
              }
            />
          )}
        </Space>
      </Card>

      <Row gutter={[16,16]}>
        <Col xs={12} lg={8}><Card><Statistic title="30天销售额" value={s.total_sales||0} prefix="₽" precision={2}/></Card></Col>
        <Col xs={12} lg={8}><Card><Statistic title="30天净收入" value={s.net_revenue||0} prefix="₽" precision={2} valueStyle={{color:'#3f8600'}}/></Card></Col>
        <Col xs={12} lg={8}><Card><Statistic title="30天佣金" value={s.total_commission||0} prefix="₽" precision={2} valueStyle={{color:'#faad14'}}/></Card></Col>
        <Col xs={12} lg={6}><Card><Statistic title="总订单" value={s.total_orders||0} suffix="单"/></Card></Col>
        <Col xs={12} lg={6}><Card><Statistic title="退单率" value={s.cancel_rate||0} suffix="%"/></Card></Col>
        <Col xs={12} lg={6}><Card><Statistic title="平均折扣" value={s.avg_discount||0} suffix="%"/></Card></Col>
        <Col xs={12} lg={6}><Card><Statistic title="活跃商品" value={s.active_products||0}/></Card></Col>
      </Row>
      <Card title="📈 每日报表" style={{marginTop:16}}>
        <Table dataSource={dailyData} columns={columns} rowKey="date" size="small" pagination={false} />
      </Card>
    </div>
  );
}

// ======================== APP ========================
function App() {
  const [collapsed, setCollapsed] = useState(false);
  const [page, setPage] = useState('dashboard');

  const menuItems = [
    {key:'dashboard', icon:<DashboardOutlined />, label:'仪表盘'},
    {key:'sales', icon:<BarChartOutlined />, label:'销售分析'},
    {key:'orders', icon:<ShoppingCartOutlined />, label:'订单管理'},
    {key:'stocks', icon:<InboxOutlined />, label:'库存概览'},
    {key:'reports', icon:<CloudSyncOutlined />, label:'财务报表'},
  ];

  const pages = {dashboard: Dashboard, sales: SalesAnalysis, orders: Orders, stocks: Stocks, reports: Reports};
  const PageComponent = pages[page] || Dashboard;

  return (
    <Layout style={{minHeight:'100vh'}}>
      <Sider collapsible collapsed={collapsed} onCollapse={setCollapsed} theme="dark">
        <div style={{height:64,display:'flex',alignItems:'center',justifyContent:'center',color:'#fff',fontSize:collapsed?14:18,fontWeight:'bold',borderBottom:'1px solid #333'}}>
          {collapsed ? 'WB' : 'WB 财务分析'}
        </div>
        <Menu theme="dark" mode="inline" selectedKeys={[page]} items={menuItems} onClick={({key}) => setPage(key)} />
      </Sider>
      <Layout>
        <Content style={{margin:16, padding:24, background:'#f5f5f5', minHeight:280}}>
          <PageComponent />
        </Content>
      </Layout>
    </Layout>
  );
}

export default App;
