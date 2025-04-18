# 房源聚类分析API文档

## 接口URL
`GET /house/cluster-analysis/`

---

## 请求参数

| 参数名         | 类型    | 是否必填 | 描述                                                         | 取值范围/格式                | 默认值                      | 示例         |
|----------------|---------|----------|--------------------------------------------------------------|------------------------------|-----------------------------|--------------|
| city_id        | int     | 否       | 城市ID，用于筛选特定城市的数据                               | 正整数                       | 无                          | 1            |
| area_id        | int     | 否       | 区域ID，用于筛选特定区域的数据                               | 正整数                       | 无                          | 2            |
| location_id    | int     | 否       | 位置ID，用于筛选特定位置的数据                               | 正整数                       | 无                          | 3            |
| n_clusters     | int     | 否       | 聚类数量（仅KMeans有效）                                     | 2-10                         | 3                           | 4            |
| features       | string  | 否       | 用于聚类的特征，多个特征用逗号分隔                           | price,single_price,use_area  | price,single_price,use_area | price,use_area|
| limit          | int     | 否       | 每个聚类返回的样本数量                                       | 1-100                        | 10                          | 20           |
| algorithm      | string  | 否       | 聚类算法                                                     | kmeans, dbscan               | kmeans                      | dbscan       |
| eps            | float   | 否       | DBSCAN算法的邻域半径（仅dbscan有效）                         | >0                           | 0.5                         | 0.3          |
| min_samples    | int     | 否       | DBSCAN算法的最小样本数（仅dbscan有效）                       | ≥1                           | 5                           | 3            |

**说明：**
- `features` 可选项包括：`price`（总价），`single_price`（单价），`use_area`（面积），可任意组合。
- `algorithm` 默认为 `kmeans`，如需使用 `dbscan`，需同时指定 `eps` 和 `min_samples`。

---

## 响应格式

```json
{
  "code": "200",
  "info": "聚类分析成功",
  "data": {
    "clusters": [
      {
        "cluster_id": 0,
        "count": 42,
        "avg_price": 3200000,
        "avg_single_price": 52000,
        "avg_use_area": 61.5,
        "representative_house": "阳光花园",
        "characteristics": "中高端小区，面积60-70㎡"
      }
    ],
    "samples": [
      {
        "id": 123,
        "house_name": "阳光花园",
        "city_name": "北京市",
        "localhost": "朝阳区",
        "cluster_id": 0,
        "price": 3150000,
        "single_price": 51800,
        "use_area": 62
      }
    ],
    "visualization": [
      {
        "id": 123,
        "x": 0.52,
        "y": 0.31,
        "cluster_id": 0
      }
    ]
  },
  "features": ["price", "single_price", "use_area"],
  "n_clusters": 3
}
```

## 错误响应
```json
{
  "code": "400",
  "info": "参数错误",
  "data": null
}
```

## 示例代码
```python
import requests
import matplotlib.pyplot as plt

def get_cluster_data():
    """获取聚类数据并处理"""
    url = "http://localhost:8000/cluster-analysis/"
    params = {
        "city_id": 1,
        "n_clusters": 4,
        "features": "price,single_price"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data['code'] != "200":
            print(f"请求失败: {data['info']}")
            return None
            
        return data['data']
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
        return None

def visualize_clusters(clusters):
    """可视化聚类结果"""
    plt.figure(figsize=(10, 6))
    
    for cluster in clusters:
        x = [point['x'] for point in cluster['points']]
        y = [point['y'] for point in cluster['points']]
        plt.scatter(x, y, label=f"Cluster {cluster['cluster']}")
    
    plt.xlabel("经度标准化值")
    plt.ylabel("纬度标准化值")
    plt.title("房源聚类分布")
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    clusters = get_cluster_data()
    if clusters:
        for cluster in clusters:
            print(f"Cluster {cluster['cluster']}: {cluster['count']} houses")
            print(f"Average price: {cluster['centers']['price']}")
        visualize_clusters(clusters)
```

## 使用场景
1. 分析不同价格区间的房源分布
2. 识别相似特征的房源群体
3. 为房源推荐系统提供数据支持