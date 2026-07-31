<script setup lang="ts">

import { ref } from "vue"
import axios from "axios"


// 保存上传文件
const file = ref<File | null>(null)


// 保存扫描结果
const result = ref<any>(null)


// 保存加载状态
const loading = ref(false)



// 选择文件
function chooseFile(event:any){

  file.value = event.target.files[0]

}



// 开始扫描
async function scan(){

  if(!file.value){

    alert("请选择文件")

    return

  }


  const formData = new FormData()


  formData.append(
    "file",
    file.value
  )


  try{


    loading.value = true


    const response = await axios.post(

      "http://127.0.0.1:8000/scan",

      formData,

      {
        headers:{
          "Content-Type":"multipart/form-data"
        }
      }

    )


    console.log(response.data)


    result.value = response.data



  }catch(error){


    console.log(error)


    alert("扫描失败，请检查后端服务")


  }finally{


    loading.value = false


  }


}



</script>



<template>


<div class="container">


<h1>
RuleForge-SAST
</h1>



<div class="upload">


<input

type="file"

accept=".php"

@change="chooseFile"

/>



<button

@click="scan"

>

{{loading ? "扫描中..." : "开始扫描"}}

</button>


</div>




<h2>
扫描结果
</h2>



<div v-if="result">


<div

class="vulnerability"

v-for="item in result.vulnerabilities"

:key="item.file + item.line"

>


<h3>
发现漏洞
</h3>


<p>

<b>
规则:
</b>

{{item.rule}}

</p>



<p>

<b>
文件:
</b>

{{item.file}}

</p>



<p>

<b>
位置:
</b>

第 {{item.line}} 行

</p>


</div>


</div>



<div v-else>


<p>
暂无扫描结果
</p>


</div>




</div>


</template>



<style scoped>


.container{

padding:40px;

font-family:
Arial,
sans-serif;

}



h1{

font-size:40px;

}



button{

margin-left:20px;

padding:

10px 20px;

cursor:pointer;

}



.upload{

margin-top:30px;

}



.vulnerability{


margin-top:20px;

padding:20px;

border:1px solid #ccc;

border-radius:10px;


background:#f8f8f8;


}



</style>