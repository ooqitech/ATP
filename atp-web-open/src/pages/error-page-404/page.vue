<template>
  <div class="basic-not-found">
    <basic-container>
      <div class="exception-content">
        <img :src="`${$baseUrl}image/theme/atp/error/404.png`" class="imgException" />
        <div>
          <h3 class="title" v-text="title"></h3>
          <p class="description" v-html="description"></p>
          <el-button @click="$router.replace({ path: '/' })">返回首页</el-button>
        </div>
      </div>
    </basic-container>
  </div>
</template>

<script>
import BasicContainer from '@vue-materials/basic-container'

const notFoundTitle = '抱歉，你访问的页面不存在'
const notFoundDescription = '您要找的页面没有找到，请返回首页继续浏览'
export default {
  components: { BasicContainer },
  name: 'BasicNotFound',
  data() {
    return {
      title: notFoundTitle,
      description: notFoundDescription
    }
  }
}
</script>

<style lang="scss" scoped>
$container-height: 70vh;
.exception-content {
  display: flex;
  align-items: center;
  justify-content: center;
  .title {
    color: rgb(51, 51, 51);
  }
  .description {
    color: rgb(102, 102, 102);
  }
}

@media screen and (max-width: 1199px) and (min-width: 721px) {
  .exception-content {
    .imgException {
      max-width: 180px;
      margin-right: 30px;
    }
    .title {
      font-size: 20px;
      margin: 10px 0;
    }
    .description {
      font-size: 14px;
    }
  }
}

@media screen and (min-width: 1200px) {
  .exception-content {
    min-height: $container-height;
    .imgException {
      max-width: 260px;
      margin-right: 50px;
    }
    .title {
      font-size: 24px;
      margin: 20px 0;
    }
    .description {
      font-size: 16px;
    }
  }
}
</style>
