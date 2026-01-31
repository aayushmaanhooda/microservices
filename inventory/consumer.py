from main import redis, Product
import time


key = "order_completed"
group= "inventory-group"

try:
    redis.xgroup_create(key, group)

except:
    print("Group alkready exists")


while True:
    try:
        results = redis.xreadgroup(group, key, {key: ">"}, None)
        if results != []:
            for result in results:
                obj = result[1][0][1]
                product = Product.get(obj["product_id"])
                try:
                    print(product)
                    product.quantity = product.quantity - int(obj["quantity"])
                    product.save()
                except:
                    redis.xadd("refund_order", obj, "*")

    except Exception as e:
        print(str(e))
    
    time.sleep(1)
    

    # [   ['order_completed', 
    #         [('1769833703909-0', {'pk': '01KG94Y7E28NADAWYA488PW5WH', 'product_id': '01KG93PA8VEZRD5RR239NXERWZ', 'price': '2.9', 'fee': '0.58', 'total': '3.48', 'quantity': '2', 'status': 'completed'})
    #         ]
    #     ]
    # ]