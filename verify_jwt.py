from jose import jwt

token='eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6ImRlZmF1bHQtdG9rZW4tNnB0bHQiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiZGVmYXVsdCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6IjE5YTIyZWE5LWMyNzUtMTFlNi04ZDYwLTA4MDAyN2Q4ZGU0MyIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0OmRlZmF1bHQifQ.qKJ9KPN-ggiVyjsqAolnmLZi3A4yd-S5URUyhdMyPg9WqdQDGPvFFUynrKfW27bWyiS0ac0OhrZ1UobxZeg6ewLTtHbVIPNQ5CU62tUf2-r_52UR5v0woEVwssoe4Qeguh8_LfXQhYxghghzUoZSyXoY8R_Uo1FPQOti5PG7aG8GhjhRI4Qlvxv91Bve8raPWdZVKykxvBHXAHbwVfkBZqXMfrclj2fhqfOqLqgRCBh3eJ6QeHVlEh7TPkSTnhb-wl6pZEk_yuBkmx8b3_auW3u7HXjIH-x6aUc_Q9_D0E3r0Rv_KF-Fn8N2iJtRBKqkrtEpfe9uLjvcbYGSs-4NGg'
ftoken='eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJjaGFvcy1nb2NkIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6ImRlZmF1bHQtdG9rZW4tNzB6aDMiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiZGVmYXVsdCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6ImYzNGY2NDNjLWMzYzQtMTFlNi1hMGJjLTA4MDAyN2Q4ZGU0MyIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpjaGFvcy1nb2NkOmRlZmF1bHQifQ.fVqEJB2A1aso2RBv615mUmh995R5WQ47Mny7pAr5kNffvImMk3CkgJYB4VW6sRNYdWrEyDHSzdRAIeNVqio9RmH5l8mEdyPmQqpQ9sk_XpwGgKAhZzmdZh_Cji1G0TSCXY0di_nlwA11gh6XJmcsu0_1soTGwJ-upwnhoRyTKl1XiCBYGXHkNa4_wadXnfKlzoHqc0qABbhVq9_q1y8Ff73mIweX-n5fdBFyXJzl10OtVhNkst_r8Ys9h--8J-dBFfo7mGiGn6Dr7es4ruw1X6QVTaqSKfa7scCighQvq10zKtB5Pl9p3en9aIZa6RRxaTIPlLVW6VoNnPTAjHb0tw'
key="""\
-----BEGIN CERTIFICATE-----
MIID2jCCAsKgAwIBAgIBATANBgkqhkiG9w0BAQsFADAiMSAwHgYDVQQDFBcxNzIu
MTYuMC4yNTNAMTQ4Mzc1NDAzMTAeFw0xNzAxMDcwMTUzNTJaFw0yNzAxMDUwMTUz
NTJaMBwxGjAYBgNVBAMTEWt1YmVybmV0ZXMtbWFzdGVyMIIBIjANBgkqhkiG9w0B
AQEFAAOCAQ8AMIIBCgKCAQEAtFMH44eqrc55WiB5chJMpJI67MZ5evn0ajxG/zJ+
G24EA4CqgkmIK7mZ3b12pNPvXf453Nck3dSD5tSob23w7pSibNw/ZSYiBZX9RSTL
5aC2u9RKKK27FZiph9Vy9hZbAXZe1UjQ2mq115V4l2OEVf8zwLvD8iBUnkVIj03y
FqZb9hTyAC7W1JyAKc8QUO4SgEgNJ4/wCIC0lJzMkFcoVDh9kCCuG7C45ZCTdTnW
hx79uuGu8PkJwqXbu1543IWPqczqQFsYy7GORlrljfpnzsDCA6TeUrWFY76+FAXI
yrJoXE5rgs2qZa5RxkFo0N6/MFvms1DwTFa63B5HHBcgCQIDAQABo4IBHzCCARsw
CQYDVR0TBAIwADAdBgNVHQ4EFgQUgyOPbhk+foFSXfT8xdogYToEKQwwUgYDVR0j
BEswSYAU1vyyWIsxQfUakhS9sB+Ci6Ls/nmhJqQkMCIxIDAeBgNVBAMUFzE3Mi4x
Ni4wLjI1M0AxNDgzNzU0MDMxggkAjEK+6ucoEzIwEwYDVR0lBAwwCgYIKwYBBQUH
AwEwCwYDVR0PBAQDAgWgMHkGA1UdEQRyMHCHBKwQAP2HBKwQAP2HBAsBAQGCCmt1
YmVybmV0ZXOCEmt1YmVybmV0ZXMuZGVmYXVsdIIWa3ViZXJuZXRlcy5kZWZhdWx0
LnN2Y4Ika3ViZXJuZXRlcy5kZWZhdWx0LnN2Yy5jbHVzdGVyLmxvY2FsMA0GCSqG
SIb3DQEBCwUAA4IBAQAH4sBB2hmvv/24P/WLkmqYeliNy/TnimOpvmxEiwuqHYRK
iskCDATAEMXMCjFm362N5+rK0aXXTb+AeLNqPBnmvEqAEzt+YJ042Y+6QR9PVert
1Oj6a+2HsiG0bEhpmkAkbbkfDiCZHwh/vojd5mK5QSBirHeVjEzndGx0vHKYtGjZ
1GUF524eci/EQWygCcNM3Vf7r2ynUmSTyCnKD+hw1bL2VVlQN4YFCLZqHL6lFicR
y41ySVHf0j6kLlI0dh7Qe8r5uVgJ70ZIsiLyxy0N57uGX0qo3SYPa++QCmDlsPKV
HFKZbanfSz5RTkbpeJiT5X1GeiJnRqsEQh+k+ta9
-----END CERTIFICATE-----
"""

r=jwt.decode(ftoken, key, algorithms=['RS256'])
print(r)
