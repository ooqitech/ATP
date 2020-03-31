<template>
  <d2-container>
    <el-form inline>
      <el-form-item>
        <a :href="downloadFuncTempUrl">
          <el-button type="primary">下载 【功能测试用例】xmind模板</el-button>
        </a>
      </el-form-item>
      <el-form-item>
        <a :href="downloadApiTempUrl">
          <el-button type="primary">下载 【接口测试用例】xmind模板</el-button>
        </a>
      </el-form-item>
    </el-form>
    <el-form style="width: 50%">
      <el-form-item>
        <el-upload
          name="file"
          :action="importFuncFileUrl"
          :on-success="handleAvatarSuccess"
          :before-upload="beforeAvatarUpload"
          :on-change="handleChange1"
          :file-list="fileList1"
        >
          <el-button size="small" type="warning">xmind >>> excel(功能)</el-button>
          <div slot="tip" class="el-upload__tip">只能转换上面模板格式文件</div>
        </el-upload>
      </el-form-item>
      <el-form-item>
        <el-upload
          name="file"
          :action="importApiFileUrl"
          :on-success="handleAvatarSuccess"
          :before-upload="beforeAvatarUpload"
          :on-change="handleChange2"
          :file-list="fileList2"
        >
          <el-button size="small" type="warning">xmind >>> excel(接口)</el-button>
          <div slot="tip" class="el-upload__tip">只能转换上面模板格式文件</div>
        </el-upload>
      </el-form-item>
    </el-form>
    <el-table :data="tableData" border ref="multipleTable">
      <el-table-column prop="fileName" label="文件名称"></el-table-column>
      <el-table-column label="操作">
        <template slot-scope="scope">
          <a :href="downloadUrl">
            <el-button type="text">下载</el-button>
          </a>
        </template>
      </el-table-column>
    </el-table>
  </d2-container>
</template>
<script>
export default {
  data() {
    return {
      importFuncFileUrl: '/atp/qa/xmindToExcel/func',
      importApiFileUrl: '/atp/qa/xmindToExcel/api',
      tableData: [],
      downloadUrl: '',
      downloadFuncTempUrl: '/atp/qa/download/功能测试用例模块.xmind',
      downloadApiTempUrl: '/atp/qa/download/接口测试用例模块.xmind',
      fileList1: [],
      fileList2: []
    }
  },
  methods: {
    handleAvatarSuccess(res, file) {
      this.$message.success(res.desc)
      this.tableData = res.tableData
      this.downloadUrl = '/atp/qa/download/' + res.tableData[0].fileName
    },
    beforeAvatarUpload(file) {
      console.log(file.type)
      const isXMIND = file.type === 'application/vnd.xmind.workbook'
      const isLt2M = file.size / 1024 / 1024 < 10
      console.log(file.size)

      if (!isXMIND) {
        this.$message.error('上传文件只能是 xmind 格式!')
      }
      if (!isLt2M) {
        console.log('上传模板大小不能超过10M!')
      }
      return isXMIND && isLt2M
    },
    handleChange1(file, fileList) {
      this.fileList1 = fileList.slice(-1)
    },
    handleChange2(file, fileList) {
      this.fileList2 = fileList.slice(-1)
    }
  }
}
</script>
