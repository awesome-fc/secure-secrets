## 简介

本示例演示了如何**安全的**在函数中使用密码、密钥、证书等数据。

函数计算支持使用服务角色安全的访问云服务资源，如OSS，表格存储等服务，这种方式之所以安全是因为用户不需要在函数代码或者配置里硬编码明文长期 Access Key 和密钥，而是依赖于函数计算服务在运行时根据服务角色换取临时 Token 供函数使用。但是还有一些其它数据，如访问数据库的用户名和密码，不能采用这种服务角色的方式换取。如何让函数安全的使用这些数据呢？下面的两种做法是**不推荐的**：

1. 将用户名和密码**明文**直接写在函数代码中。
2. 将用户名和密码**明文**通过函数的环境变量配置。

更好的做法是使用阿里云的密钥管理服务（KMS）将密钥加密，加密后的密钥可以使用上述方式引用，在函数需要使用的时候通过 KMS 解密使用。即使泄漏加密后的密钥，使用者还需要具备 KMS 访问权限才能解密，提供了多重安全保障。

## 使用步骤

1. 创建 KMS Key

```
➜  aliyun kms CreateKey --Description fc-secure-key
{
    "KeyMetadata": {
        "CreationDate": "2019-11-27T00:00:39Z",
        "Description": "fc-secure-key",
        "KeyId": "d14024ab-70f4-4a9b-aef9-b7794fec9cc3",
        "KeyState": "Enabled",
        "KeyUsage": "ENCRYPT/DECRYPT",
        "PrimaryKeyVersion": "c8b74ea7-551a-4a53-a4c4-f2dbd86ec3ac",
        "DeleteDate": "",
        "Creator": "1234567890",
        "Arn": "acs:kms:cn-hangzhou:1234567890:key/d14024ab-70f4-4a9b-aef9-b7794fec9cc3",
        "Origin": "Aliyun_KMS",
        "MaterialExpireTime": "",
        "ProtectionLevel": "SOFTWARE",
        "LastRotationDate": "2019-11-27T00:00:39Z",
        "AutomaticRotation": "Disabled"
    },
    "RequestId": "28ab2cab-a42f-45ff-91fa-e1ed2d7ce118"
}
```

2. 加密用户名和密码

```
➜  aliyun kms Encrypt --KeyId d14024ab-70f4-4a9b-aef9-b7794fec9cc3 --Plaintext root
{
    "KeyId": "d14024ab-70f4-4a9b-aef9-b7794fec9cc3",
    "KeyVersionId": "c8b74ea7-551a-4a53-a4c4-f2dbd86ec3ac",
    "CiphertextBlob": "YzhiNzRlYTctNTUxYS00YTUzLWE0YzQtZjJkYmQ4NmVjM2FjaC9aYzBSeDRvNGRmbW4rUURlajNMU2luMFMzS0c5VmZBQUFBQUFBQUFBQmlXd1d3K1VuQWNaYXBoM0xZd0dIUmR4bCtqZz09",
    "RequestId": "766fb113-0817-458d-8bb5-a109fcb87bea"
}

➜  aliyun kms Encrypt --KeyId d14024ab-70f4-4a9b-aef9-b7794fec9cc3 --Plaintext 123456
{
    "KeyId": "d14024ab-70f4-4a9b-aef9-b7794fec9cc3",
    "KeyVersionId": "c8b74ea7-551a-4a53-a4c4-f2dbd86ec3ac",
    "CiphertextBlob": "YzhiNzRlYTctNTUxYS00YTUzLWE0YzQtZjJkYmQ4NmVjM2FjaUJTU2l4clVQK00xZVFtTXdCaCtCYnZSOENGYVpQMjhBQUFBQUFBQUFBQ2pRbk42MUlEKzREeUpJdWpzb2xGbitjbFdXSjdZ",
    "RequestId": "08599f2c-111e-4ba4-be2a-18688c847c13"
}
```

3. 解密测试


```
➜  aliyun kms Decrypt --CiphertextBlob YzhiNzRlYTctNTUxYS00YTUzLWE0YzQtZjJkYmQ4NmVjM2FjaC9aYzBSeDRvNGRmbW4rUURlajNMU2luMFMzS0c5VmZBQUFBQUFBQUFBQmlXd1d3K1VuQWNaYXBoM0xZd0dIUmR4bCtqZz09
{
    "KeyId": "d14024ab-70f4-4a9b-aef9-b7794fec9cc3",
    "KeyVersionId": "c8b74ea7-551a-4a53-a4c4-f2dbd86ec3ac",
    "Plaintext": "root",
    "RequestId": "30adbdd0-69e5-44dc-ab1e-fb0c80d925a9"
}
➜  aliyun kms Decrypt --CiphertextBlob YzhiNzRlYTctNTUxYS00YTUzLWE0YzQtZjJkYmQ4NmVjM2FjaUJTU2l4clVQK00xZVFtTXdCaCtCYnZSOENGYVpQMjhBQUFBQUFBQUFBQ2pRbk42MUlEKzREeUpJdWpzb2xGbitjbFdXSjdZ
{
    "KeyId": "d14024ab-70f4-4a9b-aef9-b7794fec9cc3",
    "KeyVersionId": "c8b74ea7-551a-4a53-a4c4-f2dbd86ec3ac",
    "Plaintext": "123456",
    "RequestId": "c3c05963-2e95-46e8-8a70-b3d72355e1c7"
}
```

4. 使用 Fun 部署函数

```
fun deploy
```

5. 测试
```
fun invoke secureSecrets/hello

FC Invoke Start RequestId: 2c80fb28-9639-4d8c-94ce-99ed1fa6d7b9
2019-11-27T00:12:22.575Z 2c80fb28-9639-4d8c-94ce-99ed1fa6d7b9 [INFO] Decrypted user name: root, password: 123456
FC Invoke End RequestId: 2c80fb28-9639-4d8c-94ce-99ed1fa6d7b9
```