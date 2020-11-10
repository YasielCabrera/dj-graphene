from graphql_relay.node.node import from_global_id


def normalize_global_ids(model, input):
    return {**input, 'id': from_global_id(input.get('id'))[1]}
