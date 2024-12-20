// myjs.js

let currentView = 'text'; // text or tree
let lastCommand = 'none';
let currentEnv = 'prod';

$(document).ready( () => {
    $('#constructedAttributes').click(function(){
        getConstructedAttributes();
     });
     $('#applyFilters').click(function(){
        applyFilters();
     });
     $('#copyOutput').click(function(){
        copyToClipboard();
     });
    console.log('doc ready');
    loadListBoxes();
    makeViewToggle();
})

const loadListBoxes = () => {
    console.log('Load List Boxes');
    loadListBox("conList","getConnectors");
    loadListBox("attrList","getAttributes");
    loadListBox("flowRuleList","getFlowRules");
}

const loadListBox = (aSelect, aUrl) => {
    // aUrl = '/jerules/getConnectors'
    fetch(aUrl)
        // Convert response to text
        .then((response) => response.json())
        .then((data) => {
			for (const i of data.items) {
                // add list items to conList
                var option = document.createElement("option");
                option.text = i;
                option.value = i;
                $("#" + aSelect).append(option)
            }})
        .catch(console.error);
}

//environment change
$('#envList').on('change', function (e) {
    var optionSelected = $("option:selected", this);
    var valueSelected = this.value;
    console.log(optionSelected);
    console.log(valueSelected);
    currentEnv = valueSelected.toLowerCase();
    newData = changeEnv()
});

function AddOption(aSelect, aValue) {
    var option = document.createElement("option");
    option.text = aValue;
    option.value = aValue;
    $("#" + aSelect).append(option)
}

const changeEnv = () => {
    const myHeaders = new Headers();
    myHeaders.append("Content-Type", "application/json");
    const myRequest = new Request("changeEnv", {
        method: "post",
        body: JSON.stringify({ env:currentEnv }),
        headers: myHeaders,
        });

    fetch(myRequest)
        // Convert response to text
        .then((response) => response.json())
        .then((data) => {
            newData = data.item;
            // reload the list boxes
            $("#conList").empty() // empty the list first
            //<option value="allCon">*</option>
            AddOption('conList','*')
            loadListBox("conList","getConnectors");
            $("#attrList").empty() // empty the list first
            loadListBox("attrList","getAttributes");
            // <option value="allAttr">*</option>
            AddOption('attrList','*')
            $("#flowRuleList").empty() // empty the list first
            loadListBox("flowRuleList","getFlowRules");
            //<option value="allRules">*</option>
            AddOption('flowRuleList','*')
            return newData
        })
        .catch(console.error);
}


$('#chkShowAttributes').on( "click", function() {
    // run last command
    if (lastCommand == 'getConstructedAttributes') 
    {
        getConstructedAttributes();
    } 
    if (lastCommand == 'applyFilters') 
    {
        applyFilters();
    } 
});

const makeViewToggle = () => {
    // from https://www.cssscript.com/inline-toggle-button-buttonstrip/
    var instance = new ButtonStrip({
        id: 'buttonStrip-viewToggle'
    });
    instance.addButton('Text View', true, 'click', function(){
        console.log('Text View toggle');
        if (currentView == 'text' ) {
            return;
        }    
        currentView = 'text';
        $('#je_rules').empty();
        $("#outputText").html("Text View");
        if (lastCommand == 'getConstructedAttributes') 
        {
            getConstructedAttributes();
        } 
        if (lastCommand == 'applyFilters') 
        {
            applyFilters();
        } 
    });
    instance.addButton('Tree View', false, 'click', function(){
        console.log('Tree View toggle');
        if (currentView == 'tree' ) {
            return;
        }    
        currentView = 'tree';
        $("#je_rules").show();
        $("#outputText").html("Tree View");
        if (lastCommand == 'getConstructedAttributes') 
        {
            getConstructedAttributes();
        } 
        if (lastCommand == 'applyFilters') 
        {
            applyFilters();
        } 
    });
    instance.append('#viewToggle');
}

const getConstructedAttributes = () => {
    var connector = $('#conList').find(":selected").text(); 
    var attribute = $('#attrList').find(":selected").text();   
    lastCommand = 'getConstructedAttributes'  

    const myHeaders = new Headers();
    myHeaders.append("Content-Type", "application/json");
    const myRequest = new Request("getConstructedAttributes", {
        method: "post",
        body: JSON.stringify({ connector: connector, attribute:attribute,
                               view: currentView, env: currentEnv }),
        headers: myHeaders,
        });

    fetch(myRequest)
        // Convert response to text
        .then((response) => response.json())
        .then((data) => {
            newData = data.item;
            if (currentView == 'tree')
            {
                setJsTreeData(newData)
                $("#outputText").html("Associated Constructed Attributes for " + attribute);
            }
            else
            {
                $("#outputText").html(newData);
            }
        })
        .catch(console.error);
}

const applyFilters = () => {
    var connector = $('#conList').find(":selected").text(); 
    var direction = $('#dirList').find(":selected").text(); 
    var attribute = $('#attrList').find(":selected").text();     
    var flowRule = $('#flowRuleList').find(":selected").text(); 
    var showAttribute = $('#chkShowAttributes').prop('checked');
    console.log("checkbox is",showAttribute)
    lastCommand = 'applyFilters'    

    const myHeaders = new Headers();
    myHeaders.append("Content-Type", "application/json");
    const myRequest = new Request("applyFilter", {
        method: "post",
        body: JSON.stringify({ connector: connector, direction:direction,
                               attribute: attribute, flowRule:flowRule,
                               view: currentView, env: currentEnv,
                               showAttribute: showAttribute}),
        headers: myHeaders,
        });

    fetch(myRequest)
        // Convert response to text
        .then((response) => response.json())
        .then((data) => {
            newData = data.item;
            if (currentView == 'tree')
            {
                setJsTreeData(newData)
                s = "Fiter connector: " + connector
                s += " direction: " + direction 
                s += " attribute: " + attribute
                s += " flowRule: " + flowRule

                if (typeof newData == 'string') // error or no data returned
                {
                   s += " - " + newData
                }
                $("#outputText").html(s);
            }
            else
            {
                $("#outputText").html(newData);                
            }
        })
        .catch(console.error);
}

function treeView() {
	$('#je_rules').jstree({
		'core' : {
			'data' : [
			]
		}
	});
    // $('je_rules').toggle();    
}

function setJsTreeData(newData)
{
    // No matches found
    if (typeof newData == 'string')
    {
        $('#je_rules').jstree("destroy").empty(); 
        $("#outputText").html(newData);
        return;
    }
    $('#je_rules').jstree("destroy").empty(); 
    $('#je_rules').jstree
        ({
            'core' : {
                'data':newData['data']
             }
        });
}

function copyToClipboard() {
    var range = document.createRange();
    range.selectNode(document.getElementById("outputText"));
    window.getSelection().removeAllRanges(); // clear current selection
    window.getSelection().addRange(range); // to select text
    document.execCommand("copy");
    window.getSelection().removeAllRanges();// to deselect
    alert("copy to clipboard successful")
}


