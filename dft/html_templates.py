
class Visualize3DHtml:
    def __init__(self, mol_block: str):
        self.raw_html = """<html>
<head>
    <title>Molecule Visualization</title>
    <script src="https://3Dmol.csb.pitt.edu/build/3Dmol-min.js"></script>
    <style>
        body {{
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background-color: #f0f0f0;
        }}
        #molDiv {{
            width: 80vw;
            height: 80vh;
            border: 1px solid #ccc;
            background-color: white;
        }}
    </style>
</head>
<body>
    <div id="molDiv"></div>
    <script>
        var config = {{ backgroundColor: 'white' }};
        var viewer = $3Dmol.createViewer(document.getElementById('molDiv'), config);
        var molData = `{0}`;
        viewer.addModel(molData, 'sdf');
        viewer.setStyle({{}}, {{stick: {{radius: 0.15}}, sphere: {{radius: 0.3}}}});
        viewer.zoomTo();
        viewer.render();
    </script>
</body>
</html>
""".format(mol_block)
