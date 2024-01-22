import QtQuick 2.15
import QtQuick.Controls 2.15

Pane {
    id: root

    width: 600
    height: 400

    Frame {
        id: buttonsColumn

        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom

        anchors.leftMargin: 12
        anchors.rightMargin: 12

        width: 124

        background: Rectangle {
            anchors.fill: parent

            border.color: "black"
            border.width: 2
        }

        Column {
            anchors.fill: parent

            spacing: 2

            Label {
                width: parent.width
                height: 24

                horizontalAlignment: Label.AlignHCenter

                text: "Controls"
                font.bold: true
            }

            ToolSeparator {
                orientation: Qt.Horizontal; width: 0.75 * parent.width; anchors.horizontalCenter: parent.horizontalCenter;
                topPadding: 4; bottomPadding: 4;
                contentItem: Rectangle { implicitWidth: parent.width; implicitHeight: 2; color: "black" }
            }
    
            Button {
                width: parent.width
                height: 24
                text: "Move up"
                onClicked: qsModel.move_up()
            }

            Button {
                width: parent.width
                height: 24
                text: "Move down"
                onClicked: qsModel.move_down()
            }

            ToolSeparator {
                orientation: Qt.Horizontal; width: 0.75 * parent.width; anchors.horizontalCenter: parent.horizontalCenter;
                topPadding: 4; bottomPadding: 4;
                contentItem: Rectangle { implicitWidth: parent.width; implicitHeight: 2; color: "black" }
            }
            
            Button {
                width: parent.width
                height: 24
                text: "To top"
                onClicked: qsModel.move_top()
            }

            Button {
                width: parent.width
                height: 24
                text: "To bottom"
                onClicked: qsModel.move_bottom()
            }

            ToolSeparator {
                orientation: Qt.Horizontal; width: 0.75 * parent.width; anchors.horizontalCenter: parent.horizontalCenter;
                topPadding: 4; bottomPadding: 4;
                contentItem: Rectangle { implicitWidth: parent.width; implicitHeight: 2; color: "black" }
            }

            Button {
                width: parent.width
                height: 24
                text: "Edit"
            }

            Button {
                width: parent.width
                height: 24
                text: "Duplicate"
            }

            ToolSeparator {
                orientation: Qt.Horizontal; width: 0.75 * parent.width; anchors.horizontalCenter: parent.horizontalCenter;
                topPadding: 4; bottomPadding: 4;
                contentItem: Rectangle { implicitWidth: parent.width; implicitHeight: 2; color: "black" }
            }

            Switch {
                id: loopSwitch
                
                width: parent.width
                height: 24

                indicator: Rectangle {
                    implicitWidth: 26
                    implicitHeight: 14
                    x: loopSwitch.leftPadding
                    y: parent.height / 2 - height / 2
                    radius: 14
                    color: loopSwitch.checked ? "#17a81a" : "#ffffff"
                    border.color: loopSwitch.checked ? "#17a81a" : "#cccccc"

                    Rectangle {
                        x: loopSwitch.checked ? parent.width - width : 0
                        width: 14
                        height: 14
                        radius: 14
                        color: loopSwitch.down ? "#cccccc" : "#ffffff"
                        border.color: loopSwitch.checked ? (loopSwitch.down ? "#17a81a" : "#21be2b") : "#999999"
                    }
                }

                text: "Loop"
            }

            ToolSeparator {
                orientation: Qt.Horizontal; width: 0.75 * parent.width; anchors.horizontalCenter: parent.horizontalCenter;
                topPadding: 4; bottomPadding: 4;
                contentItem: Rectangle { implicitWidth: parent.width; implicitHeight: 2; color: "black" }
            }

            Button {
                width: parent.width
                height: 24
                text: "Delete"
            }

            Button {
                width: parent.width
                height: 24
                text: "Clear"
            }
        }
    }

    Frame {
        id: queueFrame

        anchors.left: buttonsColumn.right
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom

        padding: 2
        leftPadding: 0

        background: Rectangle {
            anchors.fill: parent
            color: "black"
        }

        HorizontalHeaderView {
            id: queueListHeader

            anchors.left: queueList.left
            anchors.right: queueList.right
            anchors.top: parent.top

            boundsBehavior: Flickable.StopAtBounds

            syncView: queueList
            clip: true
        }

        TableView {
            id: queueList

            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: queueListHeader.bottom
            anchors.bottom: parent.bottom

            anchors.topMargin: queueFrame.padding

            clip: true

            columnSpacing: 1
            rowSpacing: 1

            boundsBehavior: Flickable.StopAtBounds
            flickDeceleration: 1000

            model: qsModel
            delegate: queueListDelegate

            onWidthChanged: relayoutQueueListTimer.start()

            Timer {
                id: relayoutQueueListTimer

                interval: 1
                repeat: false

                onTriggered: queueList.forceLayout()
            }
        }
    }

    Component {
        id: queueListDelegate

        ItemDelegate {
            id: innerQueueListDelegate

            implicitWidth: Math.max(Math.min(column != queueList.columns - 1 ? queueListDelegateTextMetrics.width + 32 : queueList.width - x, queueList.width - x), 40)

            background: Rectangle {
                color: selected ? "lightblue" : (row % 2 == 0 ? "white" : "lightgray")
            }

            contentItem: Text {
                id: queueItem

                wrapMode: Text.Wrap
                maximumLineCount: 5

                horizontalAlignment: Text.AlignHCenter

                text: value

                ToolTip.delay: 1000
                ToolTip.timeout: 5000
                ToolTip.visible: hovered && (tooltip != undefined)
                ToolTip.text: tooltip != undefined ? tooltip : ""
            }

            TextMetrics {
                id: queueListDelegateTextMetrics
                font: queueItem.font
                text: queueItem.text
            }

            onClicked: qsModel.select(row)
        }
    }
}
