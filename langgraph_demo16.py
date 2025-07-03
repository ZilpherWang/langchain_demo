# 4、⼦图
# 在LangGraph中，⼀个Graph除了可以单独使⽤，还可以作为⼀个Node，嵌⼊到另⼀个Graph中。这种⽤法就称
# 为⼦图。通过⼦图，我们可以更好的重⽤Graph，构建更复杂的⼯作流。尤其在构建多Agent时，⾮常有⽤。在⼤
# 型项⽬中，通常都是由⼀个团队专⻔开发Agent，再通过其他团队来完整Agent整合。
# 使⽤⼦图时，基本和使⽤Node没有太多的区别。
# 唯⼀需要注意的是，当触发了SubGraph代表的Node后，实际上是相当于重新调⽤了⼀次subgraph.invoke(state)
# ⽅法。