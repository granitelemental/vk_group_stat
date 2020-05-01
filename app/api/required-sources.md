# Top 3 posts

 - URL: `/api/v1.0/stats/posts/top`
 - Parameters: 
   - `period` - values: `1d`, `1w`, `1M`, `1y` (default: `1w`)
   - `property` - values: `like`, `comment`, `repost`, `view` (default: `like`)

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

# Daily activity


 - URL: `/api/v1.0/stats/events/activity`
 - Parameters: 
   - `period` - values: `1d`, `1w`, `1M`, `1y` (default: `1w`)

 - Response:

```
{
    'ok': True,
    'data': {
        'posts': number,
        'likes': number,
        'comments': number,
        'reposts': number,
        'subscription': number,
    }
}
```

# Users distribution


## By gender
 - URL: `/api/v1.0/stats/users/distribution?property=gender`
 
 - Response:

```
{
    'ok': True,
    'data': {
        'total': number,
        'male': number,
        'female': number,
        'unknown': number,
    }
}
```

## By country
 - URL: `/api/v1.0/stats/users/distribution?property=country`   
 - Response:

```
{
    'ok': True,
    'data': {
        'total': number,
        'Russia': number,
        'Ukraine': number,
        'Kazakh': number,
        ...
    }
}
```

## By age
 - URL: `/api/v1.0/stats/users/distribution?property=age`   
 - Response:

```
{
    'ok': True,
    'data': {
        'total': number,
        '0-12': number,
        '13-18': number,
        '19-25': number,
        '25-35': number,
        ...
    }
}
```

