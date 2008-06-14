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
            var endTag = '</' + tagName + '>'
            var endTagIndex = buffer.indexOf(endTag)
            if (endTagIndex== -1) {
                return
            }
            var nodePayload= buffer.slice(tagOpenStartIndex, endTagIndex + endTag.length)
            var rootNode =parser.parseFromString(nodePayload,"text/xml");
            buffer = buffer.slice(endTagIndex + endTag.length+1)
            self.onread(rootNode.childNodes[0]);
        }
    }
}
