<template>
  <d2-container>
    <div>
      <case-edit :test-case-info="testCaseInfo" ref="caseEdit" @update-data="updateData"></case-edit>
    </div>
    <!--用ref给子组件起个名字-->
    <div>
      <el-button type="primary" @click="getMyEvent">点击父组件</el-button>
    </div>
  </d2-container>
</template>
<script>
export default {
  components: {
    'case-edit': () => import('./case-edit')
  },
  data() {
    return {
      testCaseInfo: {
        base: {
          systemId: '10',
          moduleId: '5',
          testsuiteId: '3',
          testcaseName: '这是测试用例名称',
          testcaseDesc: 'descs'
        },
        steps: [
          {
            setupInfo: [
              {
                args: {
                  用例编号: '4161'
                },
                desc: '前置执行用例',
                name: 'execution_testcase'
              }
            ],
            variableInfo: [
              {
                name: 'env_name',
                type: 'constant',
                value: 'aliuat'
              },
              {
                name: 'pageSize',
                type: 'constant',
                value: 2
              },
              {
                name: 'interfaceName',
                type: 'constant',
                value: 'demo_post_json'
              },
              {
                name: 'testCode',
                type: 'constant',
                value: '000'
              },
              {
                name: 'sql_var',
                type: 'db',
                value: 'select xxx from xxx;'
              },
              {
                name: 'func_var',
                type: 'function',
                value: 'encrypt_by_public_key',
                args: { 代加密文本: 'hello', 公钥: 'wsxedc' }
              }
            ],
            teardownInfo: [
              {
                name: 'teardown_db_operation',
                desc: '后置写入、更新、删除数据库',
                args: {
                  sql:
                    "INSERT INTO mock_service.mock_info_bak (`id`, `interface_name`, `mock_url`, `input_msg`, `output_msg`, `comment`, `is_valid`, `project`, `real_url`, `create_time`, `operator`, `content_type`, `method`) VALUES ('15', 'demo_post_json', 'http://118.178.173.48:6000/mock/service/ups/demo_post_json', '{}', '{\"desc\": \"这是一个默认返回\"}', '默认场景，请求报文默认为{}或\"\"，表示没有匹配到已配置的请求报文时，将使用该条响应报文返回。', '1', 'ups', 'http://www.baidu.com/demo_post_json', '2018-05-15 10:20:33', '王永骏', 'application/json;charset=UTF-8', 'POST');"
                }
              }
            ],
            requestInfo: {
              json: {
                merchantId: '4',
                storeId: '4',
                timestamp: '$current_timestamp'
              },
              sign: {
                desc: '加签(common)',
                name: 'add_sign_common'
              },
              type: 1
            },
            validateInfo: [
              {
                comparator: 'json_contains',
                check: 'content',
                expect: '{"code":"$testCode","tableData":[{"operator":"王永骏"}]}'
              },
              {
                comparator: 'db_validate',
                check: "SELECT simple_desc FROM mitest_platform_sit.env_info WHERE env_name='aliuat';",
                expect: 'aliuat环境'
              }
            ],
            extractInfo: [
              {
                check: 'content.tableData',
                saveAs: 'tableData'
              }
            ]
          }
        ],
        include: [
          {
            public_variables: [14, 5]
          }
        ]
      }
    }
  },
  methods: {
    getMyEvent() {
      this.$refs.caseEdit.saveTestCaseInfo()
      // 调用子组件的方法，child是上边ref起的名字，emitEvent是子组件的方法。
    },
    updateData(val) {
      console.log('组件数据', val)
    }
  }
}
</script>
