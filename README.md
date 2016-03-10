# Hierarchical Record #

## Introduction ##

A hierarchical record is a construct in memory and in various supported serialized formats meant to easily allow validation of structures which contain key value pairs where the key is a string and every field contains only one data type and has the potential to be repeatable. The python implementation of Hierarchical Records implements this by wrapping a data construct which contains a dictionary whose keys are all strings, and whose values are all lists. These lists contain values all of a certain type, and can be nested dictionaries whose values are all lists of things, recursing onwards and downwards to the required nesting depth. HierarchicalRecords simplify addressing and storing this data.

## Overview ##

The keys of a hierarchical record are, at depth0, exactly the same as dictionary keys. For example:

```python
>>> hr = HierarchicalRecord()
>>> hr['key'] = ["value"]
>>> hr['key']
['value']
>>> print(hr)
{
    "key": [
        "value"
    ]
}
```

Note that I specified the value associated with the key as a list, as is required by the specification.

This, however, is not the intended use of the HierarchicalRecord data type. Instead, let's now initialize this same data structure leveraging the intended syntax:

```python
>>> hr = HierarchicalRecord()
>>> hr['key0'] = "value"
>>> hr['key']
['value']
>>> hr['key0']
'value'
>>> print(hr)
{
    "key": [
        "value"
    ]
}
```

Notice that our data structure is exactly the same as before. However I have now added the intended index of the value to its initialization, and instead of needing to specify the value as a list the HierarchicalRecord class takes care of that business for me! I can then retrieve either the entire field (which is currently one entry) or an entry from that field, by calling the field without an appended index to retrieve the whole field, or with an appended index in order to retrieve the value at that index.
This saves several key strokes at the first level, but the functionality of the HierarchicalRecord class becomes more apparent as we leverage one of its key attributes: Every key in a HierarchicalRecord can store multiple values. Thus simplifying operations such as:

```python
>>> hr = HierarchicalRecord()
>>> hr['key0'] = "first_value"
>>> hr['key1'] = "second_value"
>>> hr['key2'] = "third_value"
>>> hr['key0']
'first_value'
>>> hr['key2']
'third_value'
>>> print(hr)
{
    "key": [
        "first_value",
        "second_value",
        "third_value"
    ]
}
```

Thus we have created a record where every key can correspond to multiple ordered values. What about the “hierarchical”? Since each keys values can be nested data structures of the same sort, we can nest fields in a hierarchical manner very easily by utilizing the dotted key syntax.

```python
>>> hr = HierarchicalRecord()
>>> hr['key0.nest0'] = "value_0"
>>> hr['key0.nest1'] = "value_1"
>>> hr['key1.nest0'] = "value_2"
>>> hr['key1.nest1'] = "value_3"
>>> hr['key0.nest0']
'value_0'
>>> hr['key0.nest1']
'value_1'
>>> hr['key1.nest0']
'value_2'
>>> hr['key1.nest1']
'value_3'
>>> hr['key0.nest']
['value_0', 'value_1']
>>> hr['key1.nest']
['value_2', 'value_3']
>>> hr['key']
[{'nest': ['value_0', 'value_1']}, {'nest': ['value_2', 'value_3']}]
>>> print(hr)
{
    "key": [
        {
            "nest": [
                "value_0",
                "value_1"
            ]
        },
        {
            "nest": [
                "value_2",
                "value_3"
            ]
        }
    ]
}
```

In this example we created two key fields, and two entries in both “key” fields called “nest.” The first of which contain value_0 and value_1 respectively, and the second of which contain value_2 and value_3 respectively. Utilizing the HierarchicalRecord class it is easy to quickly set and address values in this now rather complex data structure. A corresponding xml document that mimics this structure may appear as…

```xml
<key>
        <nest>”value_0”</nest>
        <nest>”value_1”</nest>
</key>
<key>
        <nest>”value_2”</nest>
        <nest>”value_3”</nest>
</key>
```

Because of how HierarchicalRecord stores its data it is not necessary to loop over all elements of a field in order to pick out element tags of interest for retrieval or setting. It also lends itself very well to easily accessing deeply nested values in complex data structures, and navigating them dynamically, in addition to validating field requirements and cardinalities.
HierarchicalRecords provide several helper functions for returning interesting portions of themselves. For example, with our previous record instance.

```python
>>> hr.keys()
['key0', 'key0.nest0', 'key0.nest1', 'key1', 'key1.nest0', 'key1.nest1']
>>> hr.values()
[{'nest': ['value_0', 'value_1']}, 'value_0', 'value_1', {'nest': ['value_2', 'value_3']}, 'value_2', 'value_3']
>>> hr.leaves()
[('key0.nest0', 'value_0'), ('key0.nest1', 'value_1'), ('key1.nest0', 'value_2'), ('key1.nest1', 'value_3')]
```

Or, perhaps more readably on several lines:

```python
>>> for x in hr.keys():
...     print(x)
...
key0
key0.nest0
key0.nest1
key1
key1.nest0
key1.nest1
>>> for x in hr.values():
...     print(x)
...
{'nest': ['value_0', 'value_1']}
value_0
value_1
{'nest': ['value_2', 'value_3']}
value_2
value_3
>>> for x in hr.leaves():
...     print(x)
...
('key0.nest0', 'value_0')
('key0.nest1', 'value_1')
('key1.nest0', 'value_2')
('key1.nest1', 'value_3')
```

Note that HierarchicalRecord.keys() and HierarchicalRecord.values() both print keys and values even when those keys and values are recursive. HierarchicalRecord.leaves() prints all leaf data associated with a record in two element tuples of form: (key, value).

## Specifications ##

* In the contained dictionary structure all keys must be strings, which can not include numbers as the final character, and can not include the “.” character
* When setting fields, values must always be lists
* Values left empty should be instances of the None object























