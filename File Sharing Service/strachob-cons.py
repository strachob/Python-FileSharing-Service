#!/usr/bin/env python
import pika
import sys
import subprocess

exchange = 'strachob_pictures'
queue = 'strachob_mini_que'
routing_key = 'miniturize'

print("%s --[%s]--> %s" % (exchange, routing_key, queue))
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue=queue, durable=True)
channel.queue_bind(queue=queue, exchange=exchange, routing_key=routing_key)

def callback(ch, method, properties, body):
    print(" [x] Received %r, %s" % (body, method))
    channel.basic_ack(delivery_tag=method.delivery_tag)
    decoded_body = body.decode('utf-8')
    file_path = './'+ decoded_body
    cmd = 'magick convert ' + file_path + ' -resize 64x64 ./static/icons/' + decoded_body.replace('files/','') + '.icon.png'
    subprocess.call(cmd, shell=True)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback,
                      queue=queue,
                      no_ack=False)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
