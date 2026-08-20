import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";

export default function ItemList({ items }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Saved items</CardTitle>
      </CardHeader>
      <CardContent>
        {items.length === 0 ? (
          <p className="text-sm text-muted-foreground">Nothing saved yet.</p>
        ) : (
          <div className="max-h-72 space-y-3 overflow-y-auto pr-1">
            {items.map((item, i) => (
              <div key={item.id}>
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium">{item.title}</p>
                    <p className="text-xs text-muted-foreground">
                      {new Date(item.created_at).toLocaleString()}
                    </p>
                  </div>
                  <Badge variant="secondary" className="shrink-0 uppercase">
                    {item.source_type}
                  </Badge>
                </div>
                {i < items.length - 1 && <Separator className="mt-3" />}
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
