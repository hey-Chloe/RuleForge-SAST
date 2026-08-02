# Security Report

## HIGH Risk

漏洞:

rules.php-dangerous-unserialize

CWE:

CWE-502

类型:

deserialization

文件:

test.php

行:

3

描述:

不安全反序列化漏洞

修复建议:

- 避免用户可控输入进入 unserialize
- 使用安全序列化方式
