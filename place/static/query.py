a = """
subscription configuration($input: SubscribeInput!) {
  subscribe(input: $input) {
    id
    ... on BasicMessage {
      data {
        __typename
        ... on ConfigurationMessageData {
          colorPalette {
            colors {
              hex
              index
              __typename
            }
            __typename
          }
          canvasConfigurations {
            index
            dx
            dy
            __typename
          }
          canvasWidth
          canvasHeight
          __typename
        }
      }
      __typename
    }
    __typename
  }
}
"""
b = """subscription replace($input: SubscribeInput!) {
  subscribe(input: $input) {
    id
    ... on BasicMessage {
      data {
        __typename
        ... on FullFrameMessageData {
          __typename
          name
          timestamp
        }
        ... on DiffFrameMessageData {
          __typename
          name
          currentTimestamp
          previousTimestamp
        }
      }
      __typename
    }
    __typename
  }
}
"""