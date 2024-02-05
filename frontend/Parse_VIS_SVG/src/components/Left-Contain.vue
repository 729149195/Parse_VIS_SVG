<template>
    <el-scrollbar height="100vh">
        <div class="left-container">
            <el-upload class="upload-area" drag :action="uploadUrl" multiple :on-change="handleFileChange"
                :before-upload="beforeUpload" accept=".svg" :on-preview="handlePreview" :on-remove="handleRemove"
                list-type="picture">
                <el-icon><upload-filled /></el-icon>
                <div class="el-upload__text">
                    Drop SVG file here or <em>click to upload</em>
                </div>
                <div class="el-upload__tip">Only SVG files are allowed</div>
                <div>
                </div>
            </el-upload>
            <el-progress :percentage="progress" v-if="progress" striped :color="customColorMethod"
                :show-text="true"></el-progress>
            <el-card class="box-card-current-file" shadow="hover" v-if="svgPreview">
                <img :src="svgPreview" alt="SVG Preview" class="svg-preview" />
            </el-card>
            <el-button type="primary" @click="evaluateSVG" class="evaluate-button">Process</el-button>
        </div>
    </el-scrollbar>
</template>

<script setup>
import { ref, watch } from 'vue';
import { UploadFilled } from '@element-plus/icons-vue';
import { useStore } from 'vuex';
import { ElNotification } from 'element-plus'

const uploadUrl = 'http://localhost:8000/upload'; // 后端上传地址
const evaluateUrl = 'http://localhost:8000/evaluate'; // 后端处理地址
const updatedSvg = 'http://localhost:8000/get-svg' //后端跟新svg地址
const removefile = 'http://localhost:8000/remove' //移除文件地址
const svgPreview = ref(null);
let currentPreviewFileName = ref("file_name"); // 保存当前预览的文件名
const store = useStore();
const progress = ref(0);
const customColorMethod = (percentage) => {
    if (percentage < 30) {
        return '#909399'
    }
    if (percentage < 70) {
        return '#e6a23c'
    }
    return '#67c23a'
}

const uploadSuccessd = () => {
    ElNotification({
        title: 'Success Parsed',
        // message: 'This is a success message',
        type: 'success',
        duration: 1000,
    })
}

function updateFileName(filename) {
    store.commit('setCurrentPreviewFileName', filename);
}

const handleRemove = file => {
    if (file.name === currentPreviewFileName) {
        svgPreview.value = null;
        currentPreviewFileName = null;
        notifyBackendAboutFileRemoval(file.name);
        store.commit('setGMInfoData', null);
        store.commit('setCurrentPreviewFileName', null);
        progress.value = 0;
    }
    else {
        notifyBackendAboutFileRemoval(file.name);
    }
};

const notifyBackendAboutFileRemoval = async (filename) => {
    try {
        await fetch(removefile, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ filename })
        });
        // 可以在这里处理后端的响应
    } catch (error) {
        console.error('在删除文件时通知后端时出错:', error);
    }
};

const handleFileChange = (file, fileList) => {
    if (fileList.length > 0) {
        const lastFile = fileList[fileList.length - 1];
        if (lastFile.status === 'success' && lastFile.type === 'image/svg+xml') {
            svgPreview.value = URL.createObjectURL(lastFile.raw);
            uploadedFile = lastFile.raw; // 确保此处正确设置文件
        }
    }
};

const handlePreview = async (file) => {
    svgPreview.value = URL.createObjectURL(file.raw);
    if (currentPreviewFileName != file.name) {
        progress.value = 0;
    }
    currentPreviewFileName = file.name; // 保存文件名
};

const beforeUpload = (file) => {
    return file.type === 'image/svg+xml';
};

const evaluateSVG = async () => {
    store.commit('setLoading', true);
    store.commit('setGMInfoData', null);
    store.commit('setCurrentPreviewFileName', null);
    progress.value = Math.floor(Math.random() * 10);
    try {
        const response = await fetch(evaluateUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ filename: currentPreviewFileName })  // 替换为实际的文件名
        });
        progress.value = Math.floor(Math.random() * 20);

        try {
            const response = await fetch(`http://localhost:8000/get-svg?filename=${currentPreviewFileName}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.text();
            store.commit('setSelectedSvg', data);
        } catch (error) {
            console.error('There was a problem fetching the SVG file:', error);
        }


        progress.value = Math.floor(Math.random() * 30);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        progress.value = Math.floor(Math.random() * 40);
        const data = await response.json();
        updateFileName(currentPreviewFileName)
        progress.value = Math.floor(Math.random() * 60);

        progress.value = Math.floor(Math.random() * 80);
        store.commit('setGMInfoData', data);
        progress.value = Math.floor(Math.random() * 90);
        // console.log('GMinfo.json data:', data);  // 打印响应数据
    } catch (error) {
        console.error('Error fetching GMinfo.json:', error);
    }
    progress.value = 100;
    store.commit('setLoading', false);
    uploadSuccessd()
};
</script>

<style>
.left-container {
    display: flex;
    flex-direction: column;
    height: 98vh;
    padding: 5px;
    /* margin-right: 5px; */
}

.upload-area {
    flex: 0 0 auto;
}

.svg-preview {
    max-width: 100%;
    max-height: 300px;
    margin-top: 5px;
    margin-bottom: 5px;
}

.box-card-current-file {
    margin: 5px 0 5px 0;
    padding: 0;
}
</style>
