var m=(a,b,N)=>new Promise((d,f)=>{var _=p=>{try{h(N.next(p))}catch(l){f(l)}},E=p=>{try{h(N.throw(p))}catch(l){f(l)}},h=p=>p.done?d(p.value):Promise.resolve(p.value).then(_,E);h((N=N.apply(a,b)).next())});import{u as P}from"./vxe-table-CPeNq2vn.js";import{bB as H,$ as A,bz as n,bC as $}from"./bootstrap-BHWmWfJw.js";import C from"./index-mQRJpXPa.js";import{_ as D}from"./page.vue_vue_type_script_setup_true_lang-lnQK_7D5.js";import{a4 as U,P as L,a9 as W,n as B,ax as K,aa as G,ab as M,ac as s,x as u,a7 as g,ai as T,aB as v,aj as S}from"../jse/index-index-a2lIU8i0.js";import"./css-Dmgy8YJo.js";import"./useMergedState-Rvg0HEPv.js";import"./EyeOutlined-D9BjerTM.js";import"./useFlexGapSupport-BYc9Kf_P.js";function w(a){return m(this,null,function*(){return H.get("/sensor-data/",{params:a})})}function k(){return m(this,null,function*(){return H.get("/sensor-data/latest/")})}function I(a){return m(this,null,function*(){return H.delete(`/sensor-data/${a}/`)})}const R={style:{"margin-left":"16px",color:"#666","font-size":"12px"}},rt=U({__name:"index",setup(a){const b={columns:[{title:"序号",type:"seq",width:80},{field:"timestamp",title:"时间戳",width:180,formatter:({cellValue:t})=>t?new Date(t).toLocaleString("zh-CN"):""},{field:"LDC_1",title:"#1机负荷",width:100,formatter:({cellValue:t})=>t?Number(t).toFixed(0):""},{field:"LDC_2",title:"#2机负荷",width:100,formatter:({cellValue:t})=>t?Number(t).toFixed(0):""},{field:"LDC_3",title:"#3机负荷",width:100,formatter:({cellValue:t})=>t?Number(t).toFixed(0):""},{field:"LDC_4",title:"#4机负荷",width:100,formatter:({cellValue:t})=>t?Number(t).toFixed(0):""},{field:"S5_01",title:"#1机五抽压力",width:120,formatter:({cellValue:t})=>t?Number(t).toFixed(3):""},{field:"S5_02",title:"#2机五抽压力",width:120,formatter:({cellValue:t})=>t?Number(t).toFixed(3):""},{field:"S5_0301",title:"#3机五抽一路压力",width:140,formatter:({cellValue:t})=>t?Number(t).toFixed(3):""},{field:"S5_0302",title:"#3机五抽二路压力",width:140,formatter:({cellValue:t})=>t?Number(t).toFixed(3):""},{field:"S5_0401",title:"#4机五抽一路压力",width:140,formatter:({cellValue:t})=>t?Number(t).toFixed(3):""},{field:"S5_0402",title:"#4机五抽二路压力",width:140,formatter:({cellValue:t})=>t?Number(t).toFixed(3):""},{field:"PLAN_MONTH",title:"月供热计划(万GJ)",width:140,formatter:({cellValue:t})=>t?Number(t).toFixed(0):""},{field:"HEATSUP_DAY_HG",title:"汉沽日供热量(万GJ)",width:150,formatter:({cellValue:t})=>t?Number(t).toFixed(2):""},{field:"HEATSUP_DAY_STC",title:"生态城日供热量(万GJ)",width:160,formatter:({cellValue:t})=>t?Number(t).toFixed(2):""},{field:"HEATSUP_DAY_NH",title:"宁河日供热量(万GJ)",width:150,formatter:({cellValue:t})=>t?Number(t).toFixed(2):""},{field:"STEAMSUP_DAY_YC",title:"盐场日供汽量(万GJ)",width:150,formatter:({cellValue:t})=>t?Number(t).toFixed(2):""},{field:"HEATSUP_TOTAL_HG",title:"汉沽累计热量",width:120,formatter:({cellValue:t})=>t?Number(t).toFixed(0):""},{field:"HEATSUP_TOTAL_STC",title:"生态城累计热量",width:130,formatter:({cellValue:t})=>t?Number(t).toFixed(0):""},{field:"HEATSUP_TOTAL_NH",title:"宁河累计热量",width:120,formatter:({cellValue:t})=>t?Number(t).toFixed(0):""},{field:"STEAMSUP_TOTAL_YC",title:"盐场累计供汽量",width:130,formatter:({cellValue:t})=>t?Number(t).toFixed(0):""},{field:"FEED_FLOW_HG",title:"汉沽供水流量",width:120,formatter:({cellValue:t})=>t?Number(t).toFixed(0):""},{field:"FEED_FLOW_STC",title:"生态城供水流量",width:130,formatter:({cellValue:t})=>t?Number(t).toFixed(0):""},{field:"FEED_FLOW_NH",title:"宁河供水流量",width:120,formatter:({cellValue:t})=>t?Number(t).toFixed(0):""},{field:"BACK_FLOW_HG",title:"汉沽回水流量",width:120,formatter:({cellValue:t})=>t?Number(t).toFixed(0):""},{field:"BACK_FLOW_STC",title:"生态城回水流量",width:130,formatter:({cellValue:t})=>t?Number(t).toFixed(0):""},{field:"BACK_FLOW_NH",title:"宁河回水流量",width:120,formatter:({cellValue:t})=>t?Number(t).toFixed(0):""},{field:"FEED_P_HG",title:"汉沽供水压力",width:120,formatter:({cellValue:t})=>t?Number(t).toFixed(2):""},{field:"FEED_P_STC",title:"生态城供水压力",width:130,formatter:({cellValue:t})=>t?Number(t).toFixed(2):""},{field:"FEED_P_NH",title:"宁河供水压力",width:120,formatter:({cellValue:t})=>t?Number(t).toFixed(2):""},{field:"BACK_P_HG",title:"汉沽回水压力",width:120,formatter:({cellValue:t})=>t?Number(t).toFixed(2):""},{field:"BACK_P_STC",title:"生态城回水压力",width:130,formatter:({cellValue:t})=>t?Number(t).toFixed(2):""},{field:"BACK_P_NH",title:"宁河回水压力",width:120,formatter:({cellValue:t})=>t?Number(t).toFixed(2):""},{field:"HEATNOW_HG",title:"汉沽实时热量",width:120,formatter:({cellValue:t})=>t?Number(t).toFixed(0):""},{field:"HEATNOW_STC",title:"生态城实时热量",width:130,formatter:({cellValue:t})=>t?Number(t).toFixed(0):""},{field:"HEATNOW_NH",title:"宁河实时热量",width:120,formatter:({cellValue:t})=>t?Number(t).toFixed(0):""},{field:"FEED_T_HG",title:"汉沽供水温度",width:120,formatter:({cellValue:t})=>t?Number(t).toFixed(0):""},{field:"FEED_T_STC",title:"生态城供水温度",width:130,formatter:({cellValue:t})=>t?Number(t).toFixed(0):""},{field:"FEED_T_NH",title:"宁河供水温度",width:120,formatter:({cellValue:t})=>t?Number(t).toFixed(0):""},{field:"BACK_T_HG",title:"汉沽回水温度",width:120,formatter:({cellValue:t})=>t?Number(t).toFixed(0):""},{field:"BACK_T_STC",title:"生态城回水温度",width:130,formatter:({cellValue:t})=>t?Number(t).toFixed(0):""},{field:"BACK_T_NH",title:"宁河回水温度",width:120,formatter:({cellValue:t})=>t?Number(t).toFixed(0):""},{field:"DRAIN_BH_03",title:"#3机滨海热网疏水流量",width:170,formatter:({cellValue:t})=>t?Number(t).toFixed(2):""},{field:"DRAIN_BH_04",title:"#4机滨海热网疏水流量",width:170,formatter:({cellValue:t})=>t?Number(t).toFixed(2):""},{field:"DRAIN_NH_03",title:"#3机宁河热网疏水流量",width:170,formatter:({cellValue:t})=>t?Number(t).toFixed(2):""},{field:"DRAIN_NH_04",title:"#4机宁河热网疏水流量",width:170,formatter:({cellValue:t})=>t?Number(t).toFixed(2):""},{field:"MAKEUP_BH_N",title:"滨海热网正常补水流量",width:160,formatter:({cellValue:t})=>t?Number(t).toFixed(2):""},{field:"MAKEUP_BH_N_TOTAL",title:"滨海热网正常补水累计",width:160,formatter:({cellValue:t})=>t?Number(t).toFixed(2):""},{field:"MAKEUP_BH_E",title:"滨海热网事故补水流量",width:160,formatter:({cellValue:t})=>t?Number(t).toFixed(2):""},{field:"MAKEUP_BH_E_TOTAL",title:"滨海热网事故补水累计",width:160,formatter:({cellValue:t})=>t?Number(t).toFixed(2):""},{field:"MAKEUP_NH_N",title:"宁河热网正常补水流量",width:160,formatter:({cellValue:t})=>t?Number(t).toFixed(2):""},{field:"MAKEUP_NH_N_TOTAL",title:"宁河热网正常补水累计",width:160,formatter:({cellValue:t})=>t?Number(t).toFixed(2):""},{field:"MAKEUP_NH_E",title:"宁河热网事故补水流量",width:160,formatter:({cellValue:t})=>t?Number(t).toFixed(2):""},{field:"MAKEUP_NH_E_TOTAL",title:"宁河热网事故补水累计",width:160,formatter:({cellValue:t})=>t?Number(t).toFixed(2):""},{field:"STEAMNOW_YC",title:"盐场实时流量",width:120,formatter:({cellValue:t})=>t?Number(t).toFixed(2):""},{field:"U1_FLOW",title:"#1海淡抽汽流量",width:130,formatter:({cellValue:t})=>t?Number(t).toFixed(2):""},{field:"U2_FLOW",title:"#2海淡抽汽流量",width:130,formatter:({cellValue:t})=>t?Number(t).toFixed(2):""},{field:"U3_FLOW",title:"#3海淡抽汽流量",width:130,formatter:({cellValue:t})=>t?Number(t).toFixed(2):""},{field:"U4_FLOW",title:"#4海淡抽汽流量",width:130,formatter:({cellValue:t})=>t?Number(t).toFixed(2):""},{field:"U5_FLOW",title:"#5海淡抽汽流量",width:130,formatter:({cellValue:t})=>t?Number(t).toFixed(2):""},{field:"U6_FLOW",title:"#6海淡抽汽流量",width:130,formatter:({cellValue:t})=>t?Number(t).toFixed(2):""},{field:"U7_FLOW",title:"#7海淡抽汽流量",width:130,formatter:({cellValue:t})=>t?Number(t).toFixed(2):""},{field:"U8_FLOW",title:"#8海淡抽汽流量",width:130,formatter:({cellValue:t})=>t?Number(t).toFixed(2):""},{field:"F_STEAM_FLOW",title:"热网首站供汽流量",width:140,formatter:({cellValue:t})=>t?Number(t).toFixed(0):""},{field:"F_DRAIN_FLOW",title:"热网首站疏水流量",width:140,formatter:({cellValue:t})=>t?Number(t).toFixed(0):""},{field:"F_FEED_T",title:"热网首站供水温度",width:140,formatter:({cellValue:t})=>t?Number(t).toFixed(0):""},{field:"F_BACK_T",title:"热网首站回水温度",width:140,formatter:({cellValue:t})=>t?Number(t).toFixed(0):""},{fixed:"right",slots:{default:"action"},title:"操作",width:160}],height:600,keepSource:!0,pagerConfig:{enabled:!0,pageSize:20},proxyConfig:{ajax:{query:e=>m(null,[e],function*({page:t}){var r,o;console.log("🔍 VXE Table查询参数:",{page:t}),console.log("🔍 当前页:",t.currentPage),console.log("🔍 每页大小:",t.pageSize);try{const i=yield w({page:t.currentPage,page_size:t.pageSize});if(console.log("📡 API原始响应:",i),console.log("📡 响应类型:",typeof i),console.log("📡 响应的keys:",Object.keys(i)),!i||typeof i!="object")throw console.error("❌ API响应格式错误:",i),new Error("API响应格式错误");if(!i.hasOwnProperty("results")||!Array.isArray(i.results))throw console.error("❌ 数据格式错误，缺少results字段或results不是数组:",i),new Error("数据格式错误");if(!i.hasOwnProperty("count")||typeof i.count!="number")throw console.error("❌ 数据格式错误，缺少count字段或count不是数字:",i),new Error("数据格式错误");console.log("📡 数据数组:",i.results),console.log("📡 数据总数:",i.count);const F={items:i.results||[],total:i.count||0};return console.log("📊 表格数据转换结果:",F),console.log("📊 数据条数:",F.items.length),console.log("📊 第一条数据示例:",F.items[0]),console.log("📊 第一条数据的timestamp:",(r=F.items[0])==null?void 0:r.timestamp),console.log("📊 第一条数据的LDC_1:",(o=F.items[0])==null?void 0:o.LDC_1),F}catch(x){return console.error("❌ 数据加载失败:",x),{items:[],total:0}}})},enabled:!0,response:{result:"items",total:"total"},autoLoad:!0},toolbarConfig:{enabled:!0,refresh:!0,slots:{buttons:"toolbar-buttons"}}},[N,d]=P({gridOptions:b}),f=L(null),_=L(!0);function E(){f.value&&clearInterval(f.value),f.value=setInterval(()=>{_.value&&d.query()},3e4)}function h(){f.value&&(clearInterval(f.value),f.value=null)}function p(){_.value=!_.value,_.value?(E(),n.success("自动刷新已开启")):(h(),n.info("自动刷新已关闭"))}function l(){d.query(),n.success("数据刷新成功")}function y(){return m(this,null,function*(){var t;try{const e=yield k();console.log("Latest data response:",e),e&&e.id?(n.success("已获取最新数据"),d.query()):n.info("暂无最新数据")}catch(e){console.log("Latest data error:",e);const r=((t=e==null?void 0:e.response)==null?void 0:t.data)||e,o=(r==null?void 0:r.message)||(r==null?void 0:r.error)||"获取最新数据失败";typeof o=="string"&&o.includes("没有数据")?n.info("暂无最新数据"):n.error(typeof o=="string"?o:"获取最新数据失败")}})}function O(t){return m(this,null,function*(){if(!t.id){n.error("无法删除：缺少数据ID");return}$.confirm({title:"确认删除",content:"确定要删除这条传感器数据吗？",onOk:()=>m(null,null,function*(){try{yield I(t.id),n.success("删除成功"),d.query()}catch(e){n.error("删除失败")}})})})}function c(t){const e=o=>{if(!o)return"-";try{return new Date(o).toLocaleString("zh-CN")}catch(x){return o}},r=(o,x=2)=>o==null||o===""?"-":typeof o=="number"?Number(o).toFixed(x):String(o);$.info({title:"传感器数据详情",width:1200,content:`
      <div style="max-height: 600px; overflow-y: auto; padding: 16px;">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
          <div>
            <h3 style="margin-bottom: 12px; color: #1890ff;">基础信息</h3>
            <p><strong>时间戳:</strong> ${e(t.timestamp)}</p>
            
            <h3 style="margin: 16px 0 12px 0; color: #1890ff;">机组负荷</h3>
            <p><strong>#1机负荷:</strong> ${r(t.LDC_1,0)}</p>
            <p><strong>#2机负荷:</strong> ${r(t.LDC_2,0)}</p>
            <p><strong>#3机负荷:</strong> ${r(t.LDC_3,0)}</p>
            <p><strong>#4机负荷:</strong> ${r(t.LDC_4,0)}</p>
            
            <h3 style="margin: 16px 0 12px 0; color: #1890ff;">机组五抽压力</h3>
            <p><strong>#1机五抽压力:</strong> ${r(t.S5_01,3)}</p>
            <p><strong>#2机五抽压力:</strong> ${r(t.S5_02,3)}</p>
            <p><strong>#3机五抽一路压力:</strong> ${r(t.S5_0301,3)}</p>
            <p><strong>#3机五抽二路压力:</strong> ${r(t.S5_0302,3)}</p>
            <p><strong>#4机五抽一路压力:</strong> ${r(t.S5_0401,3)}</p>
            <p><strong>#4机五抽二路压力:</strong> ${r(t.S5_0402,3)}</p>
            
            <h3 style="margin: 16px 0 12px 0; color: #1890ff;">供热计划</h3>
            <p><strong>月供热计划(万GJ):</strong> ${r(t.PLAN_MONTH,0)}</p>
            
            <h3 style="margin: 16px 0 12px 0; color: #1890ff;">日供热量</h3>
            <p><strong>汉沽日供热量(万GJ):</strong> ${r(t.HEATSUP_DAY_HG,2)}</p>
            <p><strong>生态城日供热量(万GJ):</strong> ${r(t.HEATSUP_DAY_STC,2)}</p>
            <p><strong>宁河日供热量(万GJ):</strong> ${r(t.HEATSUP_DAY_NH,2)}</p>
            <p><strong>盐场日供汽量(万GJ):</strong> ${r(t.STEAMSUP_DAY_YC,2)}</p>
            
            <h3 style="margin: 16px 0 12px 0; color: #1890ff;">累计热量</h3>
            <p><strong>汉沽累计热量:</strong> ${r(t.HEATSUP_TOTAL_HG,0)}</p>
            <p><strong>生态城累计热量:</strong> ${r(t.HEATSUP_TOTAL_STC,0)}</p>
            <p><strong>宁河累计热量:</strong> ${r(t.HEATSUP_TOTAL_NH,0)}</p>
            <p><strong>盐场累计供汽量:</strong> ${r(t.STEAMSUP_TOTAL_YC,0)}</p>
            
            <h3 style="margin: 16px 0 12px 0; color: #1890ff;">供水流量</h3>
            <p><strong>汉沽供水流量:</strong> ${r(t.FEED_FLOW_HG,0)}</p>
            <p><strong>生态城供水流量:</strong> ${r(t.FEED_FLOW_STC,0)}</p>
            <p><strong>宁河供水流量:</strong> ${r(t.FEED_FLOW_NH,0)}</p>
            
            <h3 style="margin: 16px 0 12px 0; color: #1890ff;">回水流量</h3>
            <p><strong>汉沽回水流量:</strong> ${r(t.BACK_FLOW_HG,0)}</p>
            <p><strong>生态城回水流量:</strong> ${r(t.BACK_FLOW_STC,0)}</p>
            <p><strong>宁河回水流量:</strong> ${r(t.BACK_FLOW_NH,0)}</p>
          </div>
          
          <div>
            <h3 style="margin-bottom: 12px; color: #1890ff;">供水压力</h3>
            <p><strong>汉沽供水压力:</strong> ${r(t.FEED_P_HG,2)}</p>
            <p><strong>生态城供水压力:</strong> ${r(t.FEED_P_STC,2)}</p>
            <p><strong>宁河供水压力:</strong> ${r(t.FEED_P_NH,2)}</p>
            
            <h3 style="margin: 16px 0 12px 0; color: #1890ff;">回水压力</h3>
            <p><strong>汉沽回水压力:</strong> ${r(t.BACK_P_HG,2)}</p>
            <p><strong>生态城回水压力:</strong> ${r(t.BACK_P_STC,2)}</p>
            <p><strong>宁河回水压力:</strong> ${r(t.BACK_P_NH,2)}</p>
            
            <h3 style="margin: 16px 0 12px 0; color: #1890ff;">实时热量</h3>
            <p><strong>汉沽实时热量:</strong> ${r(t.HEATNOW_HG,0)}</p>
            <p><strong>生态城实时热量:</strong> ${r(t.HEATNOW_STC,0)}</p>
            <p><strong>宁河实时热量:</strong> ${r(t.HEATNOW_NH,0)}</p>
            
            <h3 style="margin: 16px 0 12px 0; color: #1890ff;">供水温度</h3>
            <p><strong>汉沽供水温度:</strong> ${r(t.FEED_T_HG,0)}</p>
            <p><strong>生态城供水温度:</strong> ${r(t.FEED_T_STC,0)}</p>
            <p><strong>宁河供水温度:</strong> ${r(t.FEED_T_NH,0)}</p>
            
            <h3 style="margin: 16px 0 12px 0; color: #1890ff;">回水温度</h3>
            <p><strong>汉沽回水温度:</strong> ${r(t.BACK_T_HG,0)}</p>
            <p><strong>生态城回水温度:</strong> ${r(t.BACK_T_STC,0)}</p>
            <p><strong>宁河回水温度:</strong> ${r(t.BACK_T_NH,0)}</p>
            
            <h3 style="margin: 16px 0 12px 0; color: #1890ff;">疏水流量</h3>
            <p><strong>#3机滨海热网疏水流量:</strong> ${r(t.DRAIN_BH_03,2)}</p>
            <p><strong>#4机滨海热网疏水流量:</strong> ${r(t.DRAIN_BH_04,2)}</p>
            <p><strong>#3机宁河热网疏水流量:</strong> ${r(t.DRAIN_NH_03,2)}</p>
            <p><strong>#4机宁河热网疏水流量:</strong> ${r(t.DRAIN_NH_04,2)}</p>
            
            <h3 style="margin: 16px 0 12px 0; color: #1890ff;">滨海热网补水流量</h3>
            <p><strong>滨海热网正常补水流量:</strong> ${r(t.MAKEUP_BH_N,2)}</p>
            <p><strong>滨海热网正常补水累计:</strong> ${r(t.MAKEUP_BH_N_TOTAL,2)}</p>
            <p><strong>滨海热网事故补水流量:</strong> ${r(t.MAKEUP_BH_E,2)}</p>
            <p><strong>滨海热网事故补水累计:</strong> ${r(t.MAKEUP_BH_E_TOTAL,2)}</p>
            
            <h3 style="margin: 16px 0 12px 0; color: #1890ff;">宁河热网补水流量</h3>
            <p><strong>宁河热网正常补水流量:</strong> ${r(t.MAKEUP_NH_N,2)}</p>
            <p><strong>宁河热网正常补水累计:</strong> ${r(t.MAKEUP_NH_N_TOTAL,2)}</p>
            <p><strong>宁河热网事故补水流量:</strong> ${r(t.MAKEUP_NH_E,2)}</p>
            <p><strong>宁河热网事故补水累计:</strong> ${r(t.MAKEUP_NH_E_TOTAL,2)}</p>
            
            <h3 style="margin: 16px 0 12px 0; color: #1890ff;">盐场和海淡抽汽流量</h3>
            <p><strong>盐场实时流量:</strong> ${r(t.STEAMNOW_YC,2)}</p>
            <p><strong>#1海淡抽汽流量:</strong> ${r(t.U1_FLOW,2)}</p>
            <p><strong>#2海淡抽汽流量:</strong> ${r(t.U2_FLOW,2)}</p>
            <p><strong>#3海淡抽汽流量:</strong> ${r(t.U3_FLOW,2)}</p>
            <p><strong>#4海淡抽汽流量:</strong> ${r(t.U4_FLOW,2)}</p>
            <p><strong>#5海淡抽汽流量:</strong> ${r(t.U5_FLOW,2)}</p>
            <p><strong>#6海淡抽汽流量:</strong> ${r(t.U6_FLOW,2)}</p>
            <p><strong>#7海淡抽汽流量:</strong> ${r(t.U7_FLOW,2)}</p>
            <p><strong>#8海淡抽汽流量:</strong> ${r(t.U8_FLOW,2)}</p>
            
            <h3 style="margin: 16px 0 12px 0; color: #1890ff;">热网首站</h3>
            <p><strong>热网首站供汽流量:</strong> ${r(t.F_STEAM_FLOW,0)}</p>
            <p><strong>热网首站疏水流量:</strong> ${r(t.F_DRAIN_FLOW,0)}</p>
            <p><strong>热网首站供水温度:</strong> ${r(t.F_FEED_T,0)}</p>
            <p><strong>热网首站回水温度:</strong> ${r(t.F_BACK_T,0)}</p>
          </div>
        </div>
      </div>
    `})}return W(()=>{console.log("🚀 组件已挂载，开始初始化..."),console.log("🚀 gridApi:",d),console.log("🚀 gridApi.query函数:",d.query),B(()=>{console.log("🚀 nextTick后，准备加载数据...");try{d.query(),console.log("✅ 数据查询已触发")}catch(t){console.error("❌ 触发数据查询失败:",t)}E(),console.log("✅ 自动刷新已启动")})}),K(()=>{h()}),(t,e)=>(M(),G(g(D),{description:"实时监控电厂传感器数据，支持自动刷新和数据管理",title:"传感器数据管理"},{default:s(()=>[u(g(N),null,{"toolbar-buttons":s(()=>[u(g(C),null,{default:s(()=>[u(g(A),{type:"primary",onClick:l},{default:s(()=>e[0]||(e[0]=[T(" 手动刷新 ")])),_:1}),u(g(A),{type:_.value?"default":"primary",onClick:p},{default:s(()=>[T(S(_.value?"关闭自动刷新":"开启自动刷新"),1)]),_:1},8,["type"]),u(g(A),{onClick:y},{default:s(()=>e[1]||(e[1]=[T(" 获取最新数据 ")])),_:1}),v("div",R,S(_.value?"自动刷新：每30秒":"自动刷新：已关闭"),1)]),_:1})]),action:s(({row:r})=>[u(g(C),null,{default:s(()=>[u(g(A),{size:"small",type:"link",onClick:o=>c(r)},{default:s(()=>e[2]||(e[2]=[T(" 查看详情 ")])),_:2},1032,["onClick"]),u(g(A),{danger:"",size:"small",type:"link",onClick:o=>O(r)},{default:s(()=>e[3]||(e[3]=[T(" 删除 ")])),_:2},1032,["onClick"])]),_:2},1024)]),_:1})]),_:1}))}});export{rt as default};
