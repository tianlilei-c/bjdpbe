AI+  云网 LLM API服务

title: AI+
云网 LLM API，标准大模型接口

AI+
Base URLs，model，Authorization
POST 大模型服务接口
POST /v1/chat/completions
Body 请求参数
JSON
{
  "model": "xxxxxx",
  "messages": [
    {
      "role": "system",
      "content": "你是一个智能助手。"
    },
    {
      "role": "user",
      "content": "你好"
    }
  ],
  "max_tokens": 100,
  "presence_penalty": 1.03,
  "frequency_penalty": 1,
  "seed": null,
  "temperature": 0.01,
  "top_p": 0.95,
  "stream": false
}
请求参数
名称	位置	类型	必选	说明
Authorization	header	string	否	none
body	body	object	否	none
返回示例
200 Response
JSON
{
  "id": "string",
  "object": "string",
  "created": 0,
  "model": "string",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "string",
        "content": "string",
        "tool_calls": null
      },
      "finish_reason": "string"
    }
  ],
  "usage": {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0
  },
  "prefill_time": 0,
  "decode_time_arr": [
    0
  ]
}
返回结果
状态码	状态码含义	说明	数据模型
200	OK
none	Inline
curl 数据调用方式
Shell
curl --location --request POST 'Base URLs/v1/chat/completions' \
--header 'Authorization: xxxxxxxx' \
--header 'Content-Type: application/json' \
--data-raw '{
    "model": "xxxxxx",
    "messages": [
        {
            "role": "system",
            "content": "你是一个智能助手。"
        },
        {
            "role": "user",
            "content": "你好"
        }
    ],
    "max_tokens": 100,
    "presence_penalty": 1.03,
    "frequency_penalty": 1.0,
    "seed": null,
    "temperature": 0.01,
    "top_p": 0.95,
    "stream": false
}'

Bge-large 模型 API调用
POST /v1/embeddings
Python
#### Headers 请求参数
Authorization: Bearer {API_KEY}
Content-Type: application/json


#### Body 请求参数
{
    "model": "BAAI/bge-large-zh-v1.5",
    "input": "要进行嵌入的文本内容"
}


#### 返回示例 (200 Response)
{
    "data": [
        {
            "embedding": [...] // 嵌入向量数组
        }
    ]
}


#### CURL 调用示例
curl -X POST "http://IP:端口/v1/embeddings" \
     -H "Authorization: Bearer sk-*******************" \
     -H "Content-Type: application/json" \
     -d '{
         "model": "BAAI/bge-large-zh-v1.5",
         "input": "What is Deep Learning?"
     }'

Reranker 模型 API调用
POST /v1/rerank
Python
#### Headers 请求参数
Authorization: Bearer {API_KEY}
Content-Type: application/json


#### Body 请求参数
{
    "model": "BAAI/bge-reranker-v2-m3",
    "query": "Organic skincare products for sensitive skin",
    "top_n": 3,
    "documents": [
        "Organic skincare for sensitive skin with aloe vera and chamomile...",
        "New makeup trends focus on bold colors and innovative techniques...",
        "Bio-Hautpflege für empfindliche Haut mit Aloe Vera und Kamille..."
    ]
}


#### 返回示例 (200 Response)
{
  "results": [
    {
      "index": 0,
      "relevance_score": 0.999645471572876
    },
    {
      "index": 2,
      "relevance_score": 0.8091019988059998
    },
    {
      "index": 1,
      "relevance_score": 0.012770293280482292
    }
  ],
  "usage": {
    "prompt_tokens": 51,
    "completion_tokens": 0,
    "total_tokens": 51,
    "prompt_tokens_details": {
      "cached_tokens": 0,
      "text_tokens": 0,
      "audio_tokens": 0,
      "image_tokens": 0
    },
    "completion_tokens_details": {
      "text_tokens": 0,
      "audio_tokens": 0,
      "reasoning_tokens": 0
    },
    "input_tokens": 0,
    "output_tokens": 0,
    "input_tokens_details": null
  }
}


#### CURL 调用示例
curl -X POST "http://IP:端口/v1/rerank" \
     -H "Authorization: Bearer sk-*******************" \
     -H "Content-Type: application/json" \
     -d '{
         "model": "BAAI/bge-reranker-v2-m3",
         "query": "Organic skincare products for sensitive skin",
         "top_n": 3,
         "documents": [
             "Organic skincare for sensitive skin with aloe vera and chamomile...",
             "New makeup trends focus on bold colors and innovative techniques...",
             "Bio-Hautpflege für empfindliche Haut mit Aloe Vera und Kamille..."
         ]
     }'
可使用模型
模型列表后续会更新，请经常关注
模型	类型
Qwen2-VL-7B	多模态模型，结合了文本和图像的处理能力，响应快速
bge-reranker-v2-m3	重排序模型，通过对检索结果进行二次排序，优化文本的匹配度
bge-large-zh-v1.5（embedding）	向量模型，使中文文本能够高效地转化为计算机可以理解的向量形式，从而提高后续应用和分析的精度和效率
DeepSeek-R1-32B	推理模型，强化学习训练，精于数学、代码推理与复杂任务处理，响应快速
TianQing-72B（Qwen2.5-72B）	大语言模型，用于处理复杂的自然语言任务，响应快速

