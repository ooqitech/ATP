import request from '@/plugin/axios'
/**
 * 批量生成银行卡号
 */

export function batchGenerateCardNo(data) {
  return request({
    url: '/atp/qa/generateBankCardList',
    method: 'post',
    data
  })
}
