XMLStreamParser = function() {
    var self = this;
    var buffer = ""
    var parser=new DOMParser();

    self.onread = function(node) { }

    self.receive = function(data) {
        buffer += data
        parseBuffer()
    }

    var parseBuffer = function() {
        while (true) {
            var tagOpenStartIndex = buffer.indexOf('<')
            var tagOpenEndIndex = buffer.indexOf('>', tagOpenStartIndex)
            if (tagOpenEndIndex == -1) {
                return
            }
            var endTagNameIndex = Math.min(buffer.indexOf(' ', tagOpenStartIndex), tagOpenEndIndex)
            
            var tagName = buffer.slice(tagOpenStartIndex+1, endTagNameIndex)
            var nodePayload = ""
            // Allows detection of self contained tags like "<tag />"
            // TODO: don't make whitespace count. allow "<tag /  >"
            //       (is that valid xml?)
            if (buffer[tagOpenEndIndex-1] == '/') {
                nodePayload = buffer.slice(tagOpenStartIndex, tagOpenEndIndex+1)
            }
            else {
                var endTag = '</' + tagName + '>'
                var endTagIndex = buffer.indexOf(endTag)
                if (endTagIndex== -1) {
                    return
                }
                var nodePayload= buffer.slice(tagOpenStartIndex, endTagIndex + endTag.length)
            }
            var rootNode =parser.parseFromString(nodePayload,"text/xml");
            buffer = buffer.slice(tagOpenStartIndex + nodePayload.length)
            self.onread(rootNode.childNodes[0]);
        }
    }

}