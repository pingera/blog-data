Блог про Проверки по запросу: [ссылка на пост](https://pingera.ru/tpost/938pefyi31-blog-post-zapuskaite-proverki-iz-vashego)

### Использование скрипта

```bash
export PINGERA_API_TOKEN='YOUR_TOKEN'
python api_integration_example.py
```

Скрипт запустит единичную проверку и вернут результат в консоль.

Пример вывода:
```
--- Pingera API Endpoint Demo ---
Using API Token from environment variable: PINGERA_API_TOKEN

1. Sending POST request to execute check...
   URL: https://api.pingera.ru/v1/checks/execute
   Body: {
  "name": "Pingera web check",
  "type": "web",
  "url": "https://app.pingera.ru",
  "timeout": 10
}

--- Initial Response ---
{
  "job_id": "nifxjyphmxb0",
  "message": "Custom check execution queued successfully",
  "status": "queued"
}

Extracted Job ID: nifxjyphmxb0

2. Periodically probing job status for job ID: nifxjyphmxb0
   Polling every 3 seconds, max attempts: 20
  [1] Job ID: nifxjyphmxb0 - Status: RUNNING
  [2] Job ID: nifxjyphmxb0 - Status: COMPLETED

--- Job Completed! Final Result ---
{
  "check_id": null,
  "check_parameters": {
    "name": "Pingera web check",
    "timeout": 10,
    "type": "web",
    "url": "https://app.pingera.ru"
  },
  "completed_at": "2025-06-03T15:28:14.810013",
  "created_at": "2025-06-03T15:28:14.677238",
  "error_message": null,
  "id": "nifxjyphmxb0",
  "job_type": "custom_check",
  "result": {
    "check_id": null,
    "check_metadata": {
      "headers": {
        "Cache-Control": "public, max-age=0",
        "Connection": "keep-alive",
        "Content-Encoding": "gzip",
        "Content-Type": "text/html; charset=UTF-8",
        "Date": "Tue, 03 Jun 2025 15:28:14 GMT",
        "ETag": "W/\"7bb-19731468290\"",
        "Last-Modified": "Mon, 02 Jun 2025 15:33:14 GMT",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Transfer-Encoding": "chunked",
        "Vary": "Accept-Encoding",
        "X-Powered-By": "Express"
      },
      "status_code": 200
    },
    "check_server_id": "8q01od8rtl93",
    "job_id": "nifxjyphmxb0",
    "response_time": 47,
    "status": "ok"
  },
  "started_at": "2025-06-03T15:28:14.684825",
  "status": "completed"
}

--- Key Check Result Details ---
  Status: ok
  Response Time: 47 ms
  HTTP Status Code: 200

--- Demo Finished ---
```

