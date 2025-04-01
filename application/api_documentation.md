# 房屋信息系统API文档

本文档详细说明了房屋信息系统的API接口，用于前端Vue应用与后端Django REST API的连接和交互。

## 基础信息

- 基础URL: `http://[API_HOST]:8000/`
- 认证方式: JWT Token认证
- 响应格式: JSON

## 认证相关

所有需要认证的API都需要在请求头中添加以下字段：

```
Authorization: Bearer [access_token]
```

## 用户管理API

### 用户登录

- **URL**: `/user/login`
- **方法**: POST
- **认证要求**: 无
- **请求参数**:

```json
{
  "username": "用户名",
  "password": "密码"
}
```

- **响应示例**:

```json
{
  "code": "200",
  "info": "登录成功",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "is_staff": false
}
```

### 用户注册

- **URL**: `/user/register`
- **方法**: POST
- **认证要求**: 无
- **请求参数**:

```json
{
  "username": "用户名",
  "email": "邮箱",
  "password": "密码",
  "password2": "确认密码"
}
```

- **响应示例**:

```json
{
  "code": "201",
  "info": "注册成功",
  "user": {
    "id": 1,
    "username": "用户名",
    "email": "邮箱"
  }
}
```

### 获取用户列表

- **URL**: `/user/userlist`
- **方法**: GET
- **认证要求**: JWT认证
- **请求参数**:
  - `username` (可选): 要查找的用户名

- **响应示例**:

```json
{
  "code": "200",
  "info": "获取用户列表成功",
  "count": 10,
  "data": [
    {
      "id": 1,
      "username": "用户名",
      "email": "邮箱",
      "date_joined": "2023-01-01T00:00:00Z",
      "last_login": "2023-01-02T00:00:00Z"
    }
  ]
}
```

### 获取当前用户信息

- **URL**: `/user/userinfo`
- **方法**: GET
- **认证要求**: JWT认证
- **响应示例**:

```json
{
  "code": 200,
  "info": "获取成功",
  "data": {
    "id": 1,
    "username": "用户名",
    "email": "邮箱",
    "date_joined": "2023-01-01T00:00:00Z",
    "last_login": "2023-01-02T00:00:00Z"
  }
}
```

### 修改密码

- **URL**: `/user/userinfo`
- **方法**: PUT
- **认证要求**: JWT认证
- **请求参数**:

```json
{
  "old_password": "旧密码",
  "new_password": "新密码",
  "new_password2": "确认新密码"
}
```

- **响应示例**:

```json
{
  "code": 200,
  "info": "密码修改成功"
}
```

### 修改个人信息

- **URL**: `/user/userinfo`
- **方法**: PATCH
- **认证要求**: JWT认证
- **请求参数**:

```json
{
  "username": "新用户名",
  "email": "新邮箱"
}
```

- **响应示例**:

```json
{
  "code": 200,
  "info": "修改成功",
  "data": {
    "id": 1,
    "username": "新用户名",
    "email": "新邮箱",
    "date_joined": "2023-01-01T00:00:00Z",
    "last_login": "2023-01-02T00:00:00Z"
  }
}
```

### 管理员更新用户信息

- **URL**: `/user/admininfo/<user_id>`
- **方法**: PUT
- **认证要求**: JWT认证 (需要管理员权限)
- **请求参数**:

```json
{
  "username": "用户名",
  "email": "邮箱",
  "password": "密码",
  "is_staff": true
}
```

- **响应示例**:

```json
{
  "code": 200,
  "info": "用户信息修改成功",
  "data": {
    "username": "用户名",
    "email": "邮箱",
    "is_staff": true
  }
}
```

## 房屋信息API

### 获取房屋列表

- **URL**: `/house/citylist`
- **方法**: GET
- **认证要求**: JWT认证
- **请求参数**:
  - `city_name` (可选): 区域名称
  - `localhost` (可选): 具体位置
  - `type_name` (可选): 户型
  - `floor` (可选): 楼层
  - `fitment` (可选): 装修
  - `price_min` (可选): 最低价格
  - `price_max` (可选): 最高价格
  - `single_price_min` (可选): 最低单价
  - `single_price_max` (可选): 最高单价
  - `ordering` (可选): 排序方式(price/-price/single_price/-single_price)
  - `search` (可选): 房屋名称模糊搜索
  - `city_id` (可选): 城市ID
  - `area_id` (可选): 区域ID
  - `location_id` (可选): 位置ID
  - `page` (可选): 页码，默认为1
  - `size` (可选): 每页数量，默认为30

- **响应示例**:

```json
{
  "code": "200",
  "info": "获取成功",
  "data": [
    {
      "id": 1,
      "house_name": "小区名称",
      "city_name": "所在区",
      "localhost": "具体位置",
      "price": 500,
      "type_name": "三室一厅",
      "use_area": 120.5,
      "single_price": 30000,
      "forword": "朝南",
      "floor": "高层",
      "fitment": "精装修",
      "url": "http://example.com",
      "city": "北京",
      "city_id": 1,
      "area_id": 2,
      "location_id": 3
    }
  ],
  "count": 100,
  "current_page": 1,
  "page_size": 30,
  "next": "http://[API_HOST]:8000/house/citylist?page=2",
  "previous": null
}
```

### 获取区域列表

- **URL**: `/house/areas/`
- **方法**: GET
- **认证要求**: JWT认证
- **请求参数**:
  - `city_id` (必填): 城市ID

- **响应示例**:

```json
{
  "code": "200",
  "info": "获取成功",
  "data": [
    {
      "id": 1,
      "name": "区域名称"
    }
  ]
}
```

### 获取位置列表

- **URL**: `/house/locations/`
- **方法**: GET
- **认证要求**: JWT认证
- **请求参数**:
  - `area_id` (必填): 区域ID

- **响应示例**:

```json
{
  "code": "200",
  "info": "获取成功",
  "data": [
    {
      "id": 1,
      "location": "具体位置"
    }
  ],
  "total": 10
}
```

### 获取房源数量统计

- **URL**: `/house/statistics/`
- **方法**: GET
- **认证要求**: JWT认证
- **请求参数**:
  - `city_id` (可选): 城市ID
  - `group_by` (可选): 分组方式(city/area/location)，默认为area
  - `limit` (可选): 返回数据条数限制，默认为10

- **响应示例**:

```json
{
  "code": "200",
  "info": "获取成功",
  "data": [
    {
      "name": "区域名称",
      "value": 100
    }
  ]
}
```

### 获取地区房源单价统计

- **URL**: `/house/single-price-statistics/`
- **方法**: GET
- **认证要求**: JWT认证
- **请求参数**:
  - `city_id` (可选): 城市ID
  - `group_by` (可选): 分组方式(city/area/location)，默认为area
  - `limit` (可选): 返回数据条数限制，默认为10

- **响应示例**:

```json
{
  "code": "200",
  "info": "获取成功",
  "data": [
    {
      "name": "区域名称",
      "value": 30000.50
    }
  ],
  "stat_type": "平均单价"
}
```

### 获取地区房源金额统计

- **URL**: `/house/price-statistics/`
- **方法**: GET
- **认证要求**: JWT认证
- **请求参数**:
  - `city_id` (可选): 城市ID
  - `group_by` (可选): 分组方式(city/area/location)，默认为area
  - `limit` (可选): 返回数据条数限制，默认为10

- **响应示例**:

```json
{
  "code": "200",
  "info": "获取成功",
  "data": [
    {
      "name": "区域名称",
      "value": 500.50
    }
  ],
  "stat_type": "平均价格"
}
```

### 获取房源属性统计

- **URL**: `/house/attribute-statistics/`
- **方法**: GET
- **认证要求**: JWT认证
- **请求参数**:
  - `city_id` (可选): 城市ID
  - `area_id` (可选): 区域ID
  - `attribute` (可选): 统计属性(floor/fitment/type_name/forword)，默认为floor
  - `limit` (可选): 返回数据条数限制，默认为10

- **响应示例**:

```json
{
  "code": "200",
  "info": "获取成功",
  "data": [
    {
      "name": "高层",
      "value": 50
    }
  ],
  "attribute": "楼层"
}
```

### 获取小区房源统计

- **URL**: `/house/community-statistics/`
- **方法**: GET
- **认证要求**: JWT认证
- **请求参数**:
  - `city_id` (可选): 城市ID
  - `area_id` (可选): 区域ID
  - `location_id` (可选): 位置ID
  - `limit` (可选): 返回数据条数限制，默认为10
  - `stat_type` (可选): 统计类型(count/avg_price/avg_single_price)，默认为count

- **响应示例**:

```json
{
  "code": "200",
  "info": "获取成功",
  "data": [
    {
      "name": "小区名称",
      "value": 20
    }
  ],
  "stat_type": "房源数量"
}
```

## 错误码说明

- 200: 请求成功
- 201: 创建成功
- 400: 请求参数错误
- 401: 未认证或认证失败
- 403: 权限不足
- 404: 资源不存在
- 409: 资源冲突(如用户名已存在)
- 500: 服务器内部错误

## 前端Vue连接示例

```javascript
// 使用axios进行API请求示例
import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: 'http://[API_HOST]:8000/',
  timeout: 5000
});

// 请求拦截器，添加token
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data;
  },
  error => {
    if (error.response && error.response.status === 401) {
      // 处理token过期
      localStorage.removeItem('token');
      // 跳转到登录页
      router.push('/login');
    }
    return Promise.reject(error);
  }
);

// 登录
export function login(username, password) {
  return api.post('/user/login', {
    username,
    password
  });
}

// 获取房屋列表
export function getHouseList(params) {
  return api.get('/house/citylist', { params });
}

// 获取区域列表
export function getAreaList(cityId) {
  return api.get('/house/areas/', {
    params: { city_id: cityId }
  });
}

// 获取位置列表
export function getLocationList(areaId) {
  return api.get('/house/locations/', {
    params: { area_id: areaId }
  });
}

// 获取房源数量统计
export function getHouseStatistics(params) {
  return api.get('/house/statistics/', { params });
}
```