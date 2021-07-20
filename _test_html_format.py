a="""
var viz = new Viz();
  viz.renderSVGElement($DOT_GRAPH_STRING)
  .then(function(element) {
    document.body.appendChild(element);
  })
  .catch(function(error) {
    // Create a new Viz instance (@see Caveats page for more info)
    viz = new Viz();
    // Possibly display the error
    console.error(error);
  });
"""
print(a.replace('$DOT_GRAPH_STRING','"digraph { a -> b }"'))