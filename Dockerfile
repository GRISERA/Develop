FROM neo4j:enterprise

ENV NEO4J_AUTH=neo4j/grisera
ENV NEO4J_ACCEPT_LICENSE_AGREEMENT=yes

EXPOSE 7474 7687

CMD [ "neo4j" ]
