import type {
  DashboardMetric,
  DistributionItem,
  ProjectSummary,
  RecentFinding,
  TrendPoint,
  VulnerabilityRecord,
} from '../types/dashboard'

export const projectSummary: ProjectSummary = {
  name: 'RuleForge-SAST',
  branch: 'main',
  scanStatus: '最近扫描已完成',
  scanTime: '2 分钟前',
}

export const dashboardMetrics: DashboardMetric[] = [
  {
    label: 'Critical Vulnerabilities',
    value: 3,
    helper: '较上次扫描减少 1 项',
    tone: 'critical',
  },
  {
    label: 'High Risk',
    value: 7,
    helper: '4 项等待修复验证',
    tone: 'high',
  },
  {
    label: 'Total Findings',
    value: 24,
    helper: '覆盖 3 种代码语言',
    tone: 'neutral',
  },
  {
    label: 'Rules Loaded',
    value: 18,
    helper: '规则库状态正常',
    tone: 'primary',
  },
]

export const trendPoints: TrendPoint[] = [
  { label: '06-01', value: 17 },
  { label: '06-08', value: 22 },
  { label: '06-15', value: 19 },
  { label: '06-22', value: 31 },
  { label: '06-29', value: 28 },
  { label: '07-06', value: 26 },
  { label: '07-13', value: 24 },
]

export const vulnerabilityDistribution: DistributionItem[] = [
  { label: 'Deserialization', value: 6, color: '#6f86a6' },
  { label: 'RCE', value: 5, color: '#d45d62' },
  { label: 'XSS', value: 4, color: '#d58a48' },
  { label: 'SQL Injection', value: 3, color: '#b9a153' },
  { label: 'File Upload', value: 2, color: '#708c82' },
  { label: 'Other', value: 4, color: '#a2adbd' },
]

export const vulnerabilities: VulnerabilityRecord[] = [
  {
    id: 'finding-001',
    name: 'PHP eval 动态代码执行',
    severity: 'Critical',
    ruleId: 'php-dangerous-eval',
    cwe: 'CWE-95',
    category: 'code-execution',
    language: 'PHP',
    file: 'src/Controller/DebugController.php',
    line: 48,
    status: 'Open',
    description: '用户可控输入进入 eval，攻击者可能构造任意 PHP 代码并在服务端执行。',
    fixes: [
      '移除 eval，使用明确的数据解析或业务分支处理输入',
      '不要将用户输入拼接为可执行代码',
    ],
    patchStatus: 'PENDING',
  },
  {
    id: 'finding-002',
    name: 'Java 不安全反序列化',
    severity: 'High',
    ruleId: 'java-unsafe-deserialization',
    cwe: 'CWE-502',
    category: 'deserialization',
    language: 'Java',
    file: 'service/ImportService.java',
    line: 76,
    status: 'Reviewing',
    description: 'ObjectInputStream.readObject 处理外部数据，可能触发危险对象链并执行非预期代码。',
    fixes: [
      '避免反序列化不可信来源的 Java 对象数据',
      '改用 JSON 等安全格式并对字段进行白名单校验',
    ],
    patchStatus: 'PENDING',
  },
  {
    id: 'finding-003',
    name: '用户可控 URL 服务端请求',
    severity: 'High',
    ruleId: 'php-ssrf-user-controlled-url',
    cwe: 'CWE-918',
    category: 'ssrf',
    language: 'PHP',
    file: 'app/Services/WebhookClient.php',
    line: 113,
    status: 'Open',
    description: '用户可控 URL 进入网络请求，可能访问内网服务、云元数据或其他受限资源。',
    fixes: [
      '仅允许访问经过验证的协议、域名和端口白名单',
      '阻止回环、内网及云元数据地址，并在跳转后再次校验目标',
    ],
    patchStatus: 'PENDING',
  },
  {
    id: 'finding-004',
    name: '弱哈希算法使用',
    severity: 'Medium',
    ruleId: 'php-weak-hash',
    cwe: 'CWE-328',
    category: 'weak-crypto',
    language: 'PHP',
    file: 'app/Support/Token.php',
    line: 29,
    status: 'Fixed',
    description: '安全敏感数据使用 MD5 或 SHA-1，算法抗碰撞能力不足。',
    fixes: [
      '密码存储使用 password_hash 与 password_verify',
      '完整性校验使用 SHA-256 或更强算法，并结合具体威胁模型',
    ],
    patchStatus: 'FIXED',
  },
  {
    id: 'finding-005',
    name: 'Python pickle 不安全反序列化',
    severity: 'High',
    ruleId: 'python-unsafe-pickle',
    cwe: 'CWE-502',
    category: 'deserialization',
    language: 'Python',
    file: 'worker/import_profile.py',
    line: 34,
    status: 'Open',
    description: 'pickle.loads 反序列化外部输入，恶意载荷可能在加载过程中执行任意代码。',
    fixes: [
      '不要反序列化不可信来源的 pickle 数据',
      '使用 JSON 等安全数据格式替代 pickle',
    ],
    patchStatus: 'PENDING',
  },
  {
    id: 'finding-006',
    name: 'Java SQL 字符串拼接',
    severity: 'High',
    ruleId: 'java-sql-injection',
    cwe: 'CWE-89',
    category: 'sql-injection',
    language: 'Java',
    file: 'repository/UserRepository.java',
    line: 91,
    status: 'Reviewing',
    description: 'SQL 字符串直接拼接外部数据后交给 Statement 执行，可能导致 SQL 注入。',
    fixes: [
      '使用 PreparedStatement 和参数占位符构造查询',
      '不要通过字符串拼接将外部输入加入 SQL 语句',
    ],
    patchStatus: 'PENDING',
  },
  {
    id: 'finding-007',
    name: 'PHP 弱随机数',
    severity: 'Medium',
    ruleId: 'php-weak-randomness',
    cwe: 'CWE-330',
    category: 'weak-randomness',
    language: 'PHP',
    file: 'app/Auth/ResetCode.php',
    line: 64,
    status: 'Reviewing',
    description: 'rand 或 mt_rand 生成安全敏感令牌，输出可预测且不适合密码学场景。',
    fixes: [
      '使用 random_int 生成安全范围内的随机整数',
      '使用 random_bytes 生成令牌并进行安全编码',
    ],
    patchStatus: 'PENDING',
  },
]

export const recentFindings: RecentFinding[] = vulnerabilities
  .slice(0, 5)
  .map(({ severity, ruleId, cwe, file, line, status }) => ({
    severity,
    ruleId,
    cwe,
    file,
    line,
    status,
  }))
