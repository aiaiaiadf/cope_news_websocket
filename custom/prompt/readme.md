使用方法

```python

func = selector_prompt()
func.set_system_msg(s2)
while True:
    func.set_human_msg(s1)
    get_messages = func.get_messages()
    ...
```
