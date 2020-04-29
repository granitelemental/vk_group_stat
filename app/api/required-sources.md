# Top 3 поста

 - URL: `/api/v1.0/stats/posts/top`
 - Parameters: 
   - `duration` - values: `1d`, `1w`, `1M`, `1y`

 - Response:

```
{
    'ok': True,
    'data': [
        {
            'id': string,
            'vk_id': string,
            'likes': number,
            'comments': number,
            'view': number,
            'reposts': number,
        }
        ...
    ],
}
```