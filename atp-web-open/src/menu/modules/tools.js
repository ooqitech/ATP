export default {
  path: '/tools',
  title: '工具管理',
  icon: 'wrench',
  children: (pre => [
    {
      path: `${pre}tool`,
      title: '工具集',
      icon: 'key',
      children: [
        { path: `${pre}tool-smsCodeQuery`, title: '查看验证码' },
        { path: `${pre}tool-dataClean`, title: '数据清理' },
        { path: `${pre}tool-creditWhiteList`, title: '征信白名单' },
        { path: `${pre}tool-creditAuditQuery`, title: '征信审核结果查询' },
        { path: `${pre}tool-loanDataCalculate`, title: '账务计算公式' },
        { path: `${pre}tool-loanTransfer`, title: '一键放款' },
        { path: `${pre}tool-updateLogisticsInfo`, title: '一键发货' },
        { path: `${pre}tool-batchGenerateCardNo`, title: '一键生成银行卡号' },
        { path: `${pre}tool-xmindToExcel`, title: 'xmind转excel' },
        { path: `${pre}tool-uaaLogDecrypt`, title: '埋点日志解密' },
        { path: `${pre}tool-loanDateToOverDue`, title: '构造账务逾期数据' },
        { path: `${pre}tool-loanDateToOverDueForCapitalHub`, title: '构造账务逾期数据CH' },
        { path: `${pre}tool-setMatchFund`, title: '设置资方匹配规则' },
        { path: `${pre}tool-jsonTools`, title: 'json工具集' },
        { path: `${pre}tool-sendMQ`, title: '发送MQ' },
        { path: `${pre}tool-fareIncreaseService`, title: '现金贷加价策略配置' }
      ]
    },
    {
      path: `${pre}info`,
      title: '信息查询',
      icon: 'search-plus',
      children: [
        { path: `${pre}info-qrCodeApp`, title: '客户端二维码' },
        { path: `${pre}info-hotLinksBaoSheng`, title: '宝生系统导航' }
        // { path: `${pre}info-hotLinksYaQiaoLi`, title: '雅俏丽系统导航' },
        // { path: `${pre}info-hotLinksYouMi`, title: '又米系统导航' }
      ]
    }
    /* {
        path: `${pre}integration`,
        title: '持续集成',
        icon: 'recycle',
        children: [
            { path: `${pre}integration-failReasonSet`, title: '登记失败原因' },
            { path: `${pre}integration-greenChannelSet`, title: '发布UAT绿色通道' }
        ]
    }*/
  ])('/tools/')
}
