<style scoped lang="scss" >
.limit-width {
  font-weight: bold;
}
.li-style {
  list-style: none;
  margin-bottom: 5px;
}
</style>
<template>
  <d2-container class="limit-width">
    <el-form :model="batchGenerateCardNo" ref="batchGenerateCardNo" label-width="120px" :inline="true" size="small">
      <el-form-item label="银行卡号前缀" prop="cardPrefix" :rules="[{ min: 6, max: 6, message: '长度为6位', trigger: 'blur' }]">
        <el-input v-model="batchGenerateCardNo.cardPrefix" placeholder="不填写默认621483开头" auto-complete="off" style="width: 200px"></el-input>
      </el-form-item>
      <el-form-item label="银行卡号位数" prop="cardLength" :rules="[{ min: 2, max: 2, message: '位数不小于10', trigger: 'blur' }]">
        <el-input v-model="batchGenerateCardNo.cardLength" placeholder="不填写默认16位" auto-complete="off" style="width: 200px"></el-input>
      </el-form-item>
      <el-form-item label="批量生成数量" prop="cardNum" :rules="[{ min: 1, max: 2, message: '最大生成数量99', trigger: 'blur' }]">
        <el-input v-model="batchGenerateCardNo.cardNum" placeholder="不填写默认100个" auto-complete="off" style="width: 200px"></el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="batchGenerate('batchGenerateCardNo')">生成</el-button>
        <el-button @click="resetForm('batchGenerateCardNo')">重置</el-button>
      </el-form-item>
      <el-row :gutter="10" style="margin-top: 20px;margin-left: 20px;">
        <el-col :span="4">
          <li class="li-style" v-for="item in options1" :key="item.key">{{item}}</li>
        </el-col>
        <el-col :span="4">
          <li class="li-style" v-for="item in options2" :key="item.key">{{item}}</li>
        </el-col>
        <el-col :span="4">
          <li class="li-style" v-for="item in options3" :key="item.key">{{item}}</li>
        </el-col>
        <el-col :span="4">
          <li class="li-style" v-for="item in options4" :key="item.key">{{item}}</li>
        </el-col>
        <el-col :span="4">
          <li class="li-style" v-for="item in options5" :key="item.key">{{item}}</li>
        </el-col>
        <el-col :span="4">
          <li class="li-style" v-for="item in options6" :key="item.key">{{item}}</li>
        </el-col>
      </el-row>
    </el-form>
  </d2-container>
</template>
<script>
import { batchGenerateCardNo } from '@/api/tools/tool-batchGenerateCardNo'

export default {
  data() {
    return {
      // 当前表单默认值
      batchGenerateCardNo: {
        cardPrefix: '',
        cardLength: '',
        cardNum: ''
      },
      options1: [],
      options2: [],
      options3: [],
      options4: [],
      options5: [],
      options6: []
    }
  },
  methods: {
    batchGenerate(formName) {
      this.$refs[formName].validate(valid => {
        if (valid) {
          let cardPrefix = this.batchGenerateCardNo.cardPrefix !== '' ? this.batchGenerateCardNo.cardPrefix : '621483'
          let cardLength = this.batchGenerateCardNo.cardLength !== '' ? this.batchGenerateCardNo.cardLength : '16'
          let cardNum = this.batchGenerateCardNo.cardNum !== '' ? this.batchGenerateCardNo.cardNum : '100'
          this.loadData(cardPrefix, cardLength, cardNum).then(val => {
            if (val) {
              this.handleData(val)
            } else {
              return false
            }
          })
        } else {
          return false
        }
      })
    },
    // 提交表单事件
    loadData(cardPrefix, cardLength, cardNum) {
      return batchGenerateCardNo({
        cardFront: cardPrefix,
        cardLength: cardLength,
        number: cardNum
      }).then(resp => {
        this.$message.success('生成成功')
        return resp.bankCardList
      })
    },
    // 处理数组分组显示
    handleData(options) {
      let len = options.length
      let num = parseInt(len / 6, 10)
      let remain = Math.round(len % 6)
      let numList = []
      for (let i = 0; i < 6; i++) {
        if (i < remain) {
          numList[i] = num + 1
        } else {
          numList[i] = num
        }
      }
      this.options1 = options.slice(0, numList[0])
      this.options2 = options.slice(numList[0], numList[0] + numList[1])
      this.options3 = options.slice(numList[0] + numList[1], numList[0] + numList[1] + numList[2])
      this.options4 = options.slice(numList[0] + numList[1] + numList[2], numList[0] + numList[1] + numList[2] + numList[3])
      this.options5 = options.slice(numList[0] + numList[1] + numList[2] + numList[3], numList[0] + numList[1] + numList[2] + numList[3] + numList[4])
      this.options6 = options.slice(numList[0] + numList[1] + numList[2] + numList[3] + numList[4], len)
    },
    // 重置表单
    resetForm(formName) {
      this.$refs[formName].resetFields()
      this.options1 = []
      this.options2 = []
      this.options3 = []
      this.options4 = []
      this.options5 = []
      this.options6 = []
    }
  }
}
</script>
