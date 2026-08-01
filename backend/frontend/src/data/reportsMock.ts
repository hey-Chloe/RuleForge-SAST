import type { ReportRecord, ReportVulnerability } from '../types/reports'

interface ReportSeed extends Omit<ReportRecord, 'findings' | 'critical' | 'high' | 'sourceLabel'> {
  vulnerabilities: ReportVulnerability[]
}

function createReport(seed: ReportSeed): ReportRecord {
  return {
    ...seed,
    findings: seed.vulnerabilities.length,
    critical: seed.vulnerabilities.filter((item) => item.severity === 'CRITICAL').length,
    high: seed.vulnerabilities.filter((item) => item.severity === 'HIGH').length,
    sourceLabel: 'Demo Data',
  }
}

export const reportsMock: ReportRecord[] = [
  createReport({
    id: 'report-local-001',
    name: 'PHP 安全扫描摘要',
    scanTarget: 'testcase/test.php',
    format: 'Markdown',
    generatedAt: '2026-07-31 16:42',
    status: 'Ready',
    vulnerabilities: [
      {
        id: 'demo-php-001',
        rule: 'php-dangerous-unserialize',
        file: 'test.php',
        line: 3,
        category: 'deserialization',
        severity: 'HIGH',
        cwe: 'CWE-502',
        description: '不安全反序列化漏洞',
        fix: [
          '避免用户可控输入进入 unserialize',
          '使用安全序列化方式',
        ],
      },
      {
        id: 'demo-php-002',
        rule: 'php-reflected-xss',
        file: 'public/search.php',
        line: 18,
        category: 'xss',
        severity: 'HIGH',
        cwe: 'CWE-79',
        description: '用户可控输入直接输出到 HTML，可能导致反射型 XSS',
        fix: [
          '输出到 HTML 前使用 htmlspecialchars 并指定正确字符集',
          '根据输出上下文采用对应的安全编码',
        ],
      },
      {
        id: 'demo-php-003',
        rule: 'php-weak-hash',
        file: 'app/Support/Token.php',
        line: 29,
        category: 'weak-crypto',
        severity: 'MEDIUM',
        cwe: 'CWE-328',
        description: 'PHP 使用 MD5 或 SHA-1 弱哈希算法',
        fix: [
          '密码存储应使用 password_hash 等专用安全函数',
          '完整性校验应使用 SHA-256 或更强的哈希算法',
        ],
      },
    ],
  }),
  createReport({
    id: 'report-local-002',
    name: 'Python Worker 扫描结果',
    scanTarget: 'worker/',
    format: 'JSON',
    generatedAt: '2026-07-30 11:18',
    status: 'Ready',
    vulnerabilities: [
      {
        id: 'demo-python-001',
        rule: 'python-dangerous-eval',
        file: 'worker/expression.py',
        line: 42,
        category: 'code-execution',
        severity: 'CRITICAL',
        cwe: 'CWE-95',
        description: '不安全的 Python eval 代码执行',
        fix: [
          '避免将用户输入或外部数据传入 eval',
          '使用 ast.literal_eval 或显式解析逻辑替代动态代码执行',
        ],
      },
      {
        id: 'demo-python-002',
        rule: 'python-unsafe-pickle',
        file: 'worker/import_profile.py',
        line: 34,
        category: 'deserialization',
        severity: 'HIGH',
        cwe: 'CWE-502',
        description: '不安全的 Python pickle 反序列化',
        fix: [
          '不要反序列化不可信来源的 pickle 数据',
          '使用 JSON 等安全数据格式替代 pickle',
        ],
      },
    ],
  }),
  createReport({
    id: 'report-local-003',
    name: 'Java 服务安全复核',
    scanTarget: 'service/src/main/java/',
    format: 'Markdown',
    generatedAt: '2026-07-29 09:35',
    status: 'Ready',
    vulnerabilities: [
      {
        id: 'demo-java-001',
        rule: 'java-sql-injection',
        file: 'repository/UserRepository.java',
        line: 91,
        category: 'sql-injection',
        severity: 'HIGH',
        cwe: 'CWE-89',
        description: 'Java Statement 直接执行字符串拼接的 SQL',
        fix: [
          '使用 PreparedStatement 和占位符构造参数化查询',
          '不要将用户输入通过字符串拼接写入 SQL 语句',
        ],
      },
      {
        id: 'demo-java-002',
        rule: 'java-command-execution',
        file: 'service/TaskRunner.java',
        line: 57,
        category: 'command-execution',
        severity: 'HIGH',
        cwe: 'CWE-78',
        description: 'Java Runtime.exec 执行外部命令可能导致命令注入',
        fix: [
          '不要将用户可控输入直接传入 Runtime.exec',
          '使用参数列表、命令白名单并避免调用系统 shell',
        ],
      },
    ],
  }),
  createReport({
    id: 'report-local-004',
    name: '上传模块修复前预览',
    scanTarget: 'app/Upload/',
    format: 'JSON',
    generatedAt: '2026-07-28 14:06',
    status: 'Draft',
    vulnerabilities: [
      {
        id: 'demo-upload-001',
        rule: 'php-user-controlled-upload-name',
        file: 'app/Upload/UploadHandler.php',
        line: 65,
        category: 'file-upload',
        severity: 'HIGH',
        cwe: 'CWE-434',
        description: '用户可控上传文件名用于存储路径，可能导致危险文件上传',
        fix: [
          '使用服务端生成的随机文件名并固定允许的文件扩展名',
          '校验文件内容和 MIME 类型并将上传文件存储在 Web 根目录之外',
        ],
      },
    ],
  }),
]
